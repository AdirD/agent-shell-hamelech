#!/usr/bin/env python3
"""Sync local skill edits across all local repos and global agent directories.

Goal: Zero deviations. Whenever a skill in this repo (skills/<name>) is edited,
this script finds all usages/installations of that skill across:
  1. Global agent skill directories (~/.agents/skills, ~/.cursor/skills, ~/.claude/skills, ~/.codex/skills, ~/.gemini/skills, etc.)
  2. Local repositories in ~/Dev (and configured dev roots) containing agent skill folders (.agents/skills, .cursor/skills, .claude/skills, .codex/skills, .gemini/skills, .opencode/skills, .agent/skills, skills/)
  3. Global & project lockfiles (~/.agents/.skill-lock.json, etc.)

Usage:
  # Check status / report deviations (dry-run, exits 1 if deviations found):
  python3 scripts/sync-local-skills.py --check

  # Sync all skills across all local repos & global agent dirs:
  python3 scripts/sync-local-skills.py --apply

  # Sync only a specific skill:
  python3 scripts/sync-local-skills.py --skill smart-comments

  # Sync based on a changed file path:
  python3 scripts/sync-local-skills.py --file skills/smart-comments/SKILL.md

  # Agent lifecycle hook mode (reads JSON from stdin, writes {} to stdout):
  python3 scripts/sync-local-skills.py --hook
"""

from __future__ import annotations

import argparse
import datetime
import filecmp
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

IGNORED_SCAN_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".cache",
    "venv",
    ".venv",
    "__pycache__",
    "vendor",
    ".turbo",
    ".gradle",
    ".idea",
    ".vscode",
    "target",
    "bin",
    "obj",
    ".terraform",
    ".serverless",
}

IGNORED_SYNC_FILES = {
    ".DS_Store",
    "Thumbs.db",
}

AGENT_DIR_NAMES = {
    ".agents",
    ".cursor",
    ".claude",
    ".codex",
    ".gemini",
    ".opencode",
    ".agent",
    "_agents",
    "_agent",
}


def find_repo_root() -> Path:
    """Find the root directory of agent-shell-hamelech."""
    cand = Path(__file__).resolve().parent.parent
    if (cand / "skills").is_dir() and (cand / "README.md").is_file():
        return cand
    return Path.cwd().resolve()


def compute_git_tree_hash(dir_path: Path) -> str:
    """Compute exact Git tree SHA for a directory (matches git rev-parse HEAD:<dir>)."""
    entries: list[tuple[bytes, bytes]] = []
    if not dir_path.is_dir():
        return ""
    items = sorted(os.listdir(dir_path))
    for name in items:
        if name in IGNORED_SYNC_FILES or name == ".git":
            continue
        p = dir_path / name
        if p.is_file():
            content = p.read_bytes()
            blob_hdr = f"blob {len(content)}\0".encode("latin1")
            sha = hashlib.sha1(blob_hdr + content).digest()
            mode = "100755" if os.access(p, os.X_OK) else "100644"
            entries.append((name.encode("utf-8"), f"{mode} {name}\0".encode("latin1") + sha))
        elif p.is_dir():
            sub_sha_hex = compute_git_tree_hash(p)
            if not sub_sha_hex:
                continue
            sha = bytes.fromhex(sub_sha_hex)
            entries.append((name.encode("utf-8") + b"/", f"40000 {name}\0".encode("latin1") + sha))

    entries.sort(key=lambda x: x[0])
    tree_data = b"".join(e[1] for e in entries)
    hdr = f"tree {len(tree_data)}\0".encode("latin1")
    return hashlib.sha1(hdr + tree_data).hexdigest()


def get_available_skills(repo_root: Path) -> dict[str, Path]:
    """Map skill name -> Path to skill folder in repo."""
    skills_dir = repo_root / "skills"
    res: dict[str, Path] = {}
    if not skills_dir.is_dir():
        return res
    for d in skills_dir.iterdir():
        if d.is_dir() and (d / "SKILL.md").is_file():
            res[d.name] = d.resolve()
    return res


def shorten_path(path: Path) -> str:
    home = Path.home()
    try:
        rel = path.relative_to(home)
        return f"~/{rel}"
    except ValueError:
        return str(path)


def find_global_skill_dirs(skill_names: set[str]) -> list[dict[str, Any]]:
    """Locate all global agent skill targets."""
    home = Path.home()
    candidates = [
        ("global (.agents)", home / ".agents" / "skills"),
        ("global (.cursor)", home / ".cursor" / "skills"),
        ("global (.claude)", home / ".claude" / "skills"),
        ("global (.codex)", home / ".codex" / "skills"),
        ("global (.gemini)", home / ".gemini" / "skills"),
        ("global (gemini-antigravity)", home / ".gemini" / "antigravity" / "skills"),
        ("global (config-agents)", home / ".config" / "agents" / "skills"),
    ]
    targets: list[dict[str, Any]] = []
    for label, base in candidates:
        if not base.is_dir():
            continue
        for s in skill_names:
            target_path = base / s
            if target_path.exists():
                targets.append({
                    "scope": "global",
                    "location_type": label,
                    "skill": s,
                    "target_path": target_path,
                    "is_symlink": target_path.is_symlink(),
                })
    return targets


def find_project_skill_dirs(repo_root: Path, skill_names: set[str], extra_roots: list[Path] | None = None) -> list[dict[str, Any]]:
    """Scan local development directories for project-level skill installations."""
    dev_roots: list[Path] = []
    
    # 1. User specified roots or env
    if extra_roots:
        dev_roots.extend(extra_roots)
    env_roots = os.environ.get("SKILLS_DEV_ROOTS")
    if env_roots:
        for r in env_roots.split(os.pathsep):
            if r.strip():
                dev_roots.append(Path(r.strip()).expanduser().resolve())
                
    # 2. Default parent and ~/Dev
    default_dev = Path.home() / "Dev"
    if default_dev.is_dir() and default_dev not in dev_roots:
        dev_roots.append(default_dev)
        
    parent_dev = repo_root.parent.resolve()
    if parent_dev.is_dir() and parent_dev not in dev_roots:
        dev_roots.append(parent_dev)

    targets: list[dict[str, Any]] = []
    seen_paths: set[str] = set()

    for dev_root in dev_roots:
        if not dev_root.is_dir():
            continue
        for root, dirs, _ in os.walk(dev_root):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORED_SCAN_DIRS]
            
            # Avoid scanning inside current repo_root
            current_p = Path(root).resolve()
            if current_p == repo_root or repo_root in current_p.parents:
                dirs[:] = []
                continue
                
            # Limit search depth to 3 levels below dev_root
            try:
                rel = current_p.relative_to(dev_root)
                if len(rel.parts) > 3:
                    dirs[:] = []
                    continue
            except ValueError:
                pass

            if current_p.name == "skills":
                parent_dir = current_p.parent
                is_agent_skills = parent_dir.name in AGENT_DIR_NAMES
                is_direct_skills = (parent_dir / ".git").is_dir() or (parent_dir / "package.json").is_file()

                if is_agent_skills or is_direct_skills:
                    for s in skill_names:
                        target_path = current_p / s
                        if target_path.exists() and (target_path / "SKILL.md").is_file():
                            norm = str(target_path.resolve()) if not target_path.is_symlink() else str(target_path)
                            if norm in seen_paths:
                                continue
                            seen_paths.add(norm)
                            
                            # Determine project name
                            project_name = parent_dir.name if not is_agent_skills else parent_dir.parent.name
                            location_label = f"project:{project_name} ({parent_dir.name}/skills)"
                            
                            targets.append({
                                "scope": "project",
                                "project": project_name,
                                "location_type": location_label,
                                "skill": s,
                                "target_path": target_path,
                                "is_symlink": target_path.is_symlink(),
                            })

    return targets


def compare_skill_folder(source_dir: Path, target_dir: Path) -> dict[str, Any]:
    """Compare a source skill folder with a target installation folder."""
    if not target_dir.exists():
        return {"status": "missing", "diff_files": [], "source_only": [], "target_only": []}

    if target_dir.is_symlink():
        try:
            target_real = target_dir.resolve()
            source_real = source_dir.resolve()
            if target_real == source_real:
                return {"status": "symlink_exact", "diff_files": [], "source_only": [], "target_only": []}
            else:
                return {"status": "symlink_other", "diff_files": [], "source_only": [], "target_only": []}
        except Exception:
            return {"status": "symlink_broken", "diff_files": [], "source_only": [], "target_only": []}

    diff_files: list[str] = []
    source_only: list[str] = []
    target_only: list[str] = []

    def recursive_cmp(src: Path, tgt: Path, rel_prefix: str = "") -> None:
        if not tgt.is_dir():
            source_only.append(rel_prefix or str(src.name))
            return

        src_items = {i for i in os.listdir(src) if i not in IGNORED_SYNC_FILES and i != ".git"}
        tgt_items = {i for i in os.listdir(tgt) if i not in IGNORED_SYNC_FILES and i != ".git"}

        for item in src_items - tgt_items:
            rel = f"{rel_prefix}/{item}" if rel_prefix else item
            source_only.append(rel)

        for item in tgt_items - src_items:
            rel = f"{rel_prefix}/{item}" if rel_prefix else item
            target_only.append(rel)

        for item in src_items & tgt_items:
            s_p = src / item
            t_p = tgt / item
            rel = f"{rel_prefix}/{item}" if rel_prefix else item
            if s_p.is_file() and t_p.is_file():
                if not filecmp.cmp(s_p, t_p, shallow=False):
                    diff_files.append(rel)
            elif s_p.is_dir() and t_p.is_dir():
                recursive_cmp(s_p, t_p, rel)
            else:
                diff_files.append(rel)

    recursive_cmp(source_dir, target_dir)

    if not diff_files and not source_only and not target_only:
        status = "in_sync"
    else:
        status = "outdated"

    return {
        "status": status,
        "diff_files": diff_files,
        "source_only": source_only,
        "target_only": target_only,
    }


def copy_skill_tree(source_dir: Path, target_dir: Path) -> list[str]:
    """Synchronize target directory with source directory, removing deleted files."""
    changes: list[str] = []
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Prune target files and directories not in source
    for root, dirs, files in os.walk(target_dir, topdown=False):
        rel = Path(root).relative_to(target_dir)
        src_root = source_dir / rel

        for f in files:
            if f in IGNORED_SYNC_FILES:
                continue
            if not (src_root / f).is_file():
                (Path(root) / f).unlink()
                changes.append(f"removed {rel / f if rel != Path('.') else f}")

        for d in dirs:
            if d in IGNORED_SYNC_FILES:
                continue
            if not (src_root / d).is_dir():
                shutil.rmtree(Path(root) / d)
                changes.append(f"removed directory {rel / d if rel != Path('.') else d}")

    # 2. Copy source files to target
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_SYNC_FILES and d != ".git"]
        rel = Path(root).relative_to(source_dir)
        tgt_root = target_dir / rel
        tgt_root.mkdir(parents=True, exist_ok=True)

        for f in files:
            if f in IGNORED_SYNC_FILES:
                continue
            src_f = Path(root) / f
            tgt_f = tgt_root / f
            if not tgt_f.exists() or not filecmp.cmp(src_f, tgt_f, shallow=False):
                shutil.copy2(src_f, tgt_f)
                changes.append(f"updated {rel / f if rel != Path('.') else f}")

    return changes


def update_lockfiles(skill_name: str, tree_sha: str) -> list[str]:
    """Update skillFolderHash and updatedAt in global & local skill lockfiles."""
    updates: list[str] = []
    lock_paths = [
        Path.home() / ".agents" / ".skill-lock.json",
    ]
    
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

    for lp in lock_paths:
        if not lp.is_file():
            continue
        try:
            data = json.loads(lp.read_text(encoding="utf-8"))
            skills = data.get("skills", {})
            if skill_name in skills:
                entry = skills[skill_name]
                old_sha = entry.get("skillFolderHash", "")
                if old_sha != tree_sha:
                    entry["skillFolderHash"] = tree_sha
                    entry["updatedAt"] = now_iso
                    lp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                    updates.append(f"{shorten_path(lp)} ({skill_name}: {old_sha[:8]} -> {tree_sha[:8]})")
        except Exception as e:
            print(f"[!] Warning: failed to update lockfile {lp}: {e}", file=sys.stderr)

    return updates


def run_sync(
    repo_root: Path,
    target_skills: set[str] | None = None,
    dry_run: bool = False,
    verbose: bool = False,
    extra_roots: list[Path] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Scan and synchronize all skill usages across global and local repos."""
    available = get_available_skills(repo_root)
    if not available:
        print("[!] No skills found in repo under skills/", file=sys.stderr)
        return 1, {"error": "no skills found"}

    selected_skill_names = set(available.keys())
    if target_skills:
        selected_skill_names = selected_skill_names.intersection(target_skills)
        if not selected_skill_names:
            print(f"[!] None of specified skills {target_skills} found in repo.", file=sys.stderr)
            return 1, {"error": "specified skills not found"}

    # Compute latest tree SHAs
    tree_shas = {s: compute_git_tree_hash(available[s]) for s in selected_skill_names}

    # Find targets
    global_targets = find_global_skill_dirs(selected_skill_names)
    project_targets = find_project_skill_dirs(repo_root, selected_skill_names, extra_roots)
    all_targets = global_targets + project_targets

    results: list[dict[str, Any]] = []
    outdated_count = 0
    synced_count = 0
    symlink_count = 0
    applied_changes_count = 0

    for t in all_targets:
        skill_name = t["skill"]
        src_path = available[skill_name]
        tgt_path = t["target_path"]
        cmp_res = compare_skill_folder(src_path, tgt_path)

        res_entry = {
            "skill": skill_name,
            "scope": t["scope"],
            "location_type": t["location_type"],
            "path": str(tgt_path),
            "display_path": shorten_path(tgt_path),
            "status": cmp_res["status"],
            "diff_files": cmp_res["diff_files"],
            "source_only": cmp_res["source_only"],
            "target_only": cmp_res["target_only"],
            "applied_changes": [],
        }

        if cmp_res["status"] == "in_sync":
            synced_count += 1
        elif cmp_res["status"] in ("symlink_exact", "symlink_other"):
            symlink_count += 1
        else:
            outdated_count += 1
            if not dry_run:
                if t["is_symlink"]:
                    pass  # Keep existing symlink intact
                else:
                    changes = copy_skill_tree(src_path, tgt_path)
                    res_entry["applied_changes"] = changes
                    applied_changes_count += len(changes)
                    res_entry["status"] = "synced_now"

        results.append(res_entry)

    # Lockfile updates
    lockfile_updates: list[str] = []
    if not dry_run:
        for s in selected_skill_names:
            sha = tree_shas[s]
            if sha:
                lockfile_updates.extend(update_lockfiles(s, sha))

    summary = {
        "total_targets": len(all_targets),
        "in_sync": synced_count,
        "symlinks": symlink_count,
        "outdated_or_deviated": outdated_count,
        "applied_changes": applied_changes_count,
        "lockfile_updates": lockfile_updates,
        "results": results,
    }

    return (1 if (dry_run and outdated_count > 0) else 0), summary


def print_report(summary: dict[str, Any], dry_run: bool, verbose: bool) -> None:
    results = summary.get("results", [])
    outdated = [r for r in results if r["status"] == "outdated"]
    synced_now = [r for r in results if r["status"] == "synced_now"]
    in_sync = [r for r in results if r["status"] in ("in_sync", "symlink_exact")]

    print("\n================================================================================")
    print(" 👑 AGENT SHEL HAMELECH — LOCAL SKILL USAGE & SYNC REPORT")
    print("================================================================================")
    print(f" Targets found:      {summary['total_targets']} installations across local repos & global agent dirs")
    print(f" Already in sync:    {summary['in_sync']} (plus {summary['symlinks']} symlinks)")
    if dry_run:
        print(f" Deviations/outdated:{summary['outdated_or_deviated']}")
    else:
        print(f" Synced now:         {len(synced_now)} installations ({summary['applied_changes']} file changes)")
    print("--------------------------------------------------------------------------------")

    if dry_run and outdated:
        print("\n❌ DEVIATIONS DETECTED (Outdated installations):")
        for r in outdated:
            diffs = []
            if r["diff_files"]:
                diffs.append(f"modified: {', '.join(r['diff_files'])}")
            if r["source_only"]:
                diffs.append(f"missing: {', '.join(r['source_only'])}")
            if r["target_only"]:
                diffs.append(f"stale: {', '.join(r['target_only'])}")
            diff_str = "; ".join(diffs) if diffs else "content mismatch"
            print(f"  • [{r['skill']}] {r['location_type']} -> {r['display_path']}")
            print(f"    ↳ {diff_str}")
        print("\nRun with --apply to synchronize all installations:")
        print("  python3 scripts/sync-local-skills.py --apply\n")
    elif not dry_run and synced_now:
        print("\n✅ SYNCHRONIZED INSTALLATIONS:")
        for r in synced_now:
            ch_count = len(r.get("applied_changes", []))
            print(f"  • [{r['skill']}] {r['location_type']} -> {r['display_path']} ({ch_count} changes)")
            if verbose:
                for ch in r.get("applied_changes", []):
                    print(f"      - {ch}")
    else:
        print("\n✨ All installed skill copies across local repos and global dirs are 100% in sync!\n")

    if summary.get("lockfile_updates"):
        print("🔒 Updated skill lockfiles:")
        for lup in summary["lockfile_updates"]:
            print(f"  • {lup}")
    print("================================================================================\n")


def handle_hook_mode(repo_root: Path) -> None:
    """Handle invocation from agent lifecycle hooks (PostToolUse, afterFileEdit)."""
    # Read stdin payload if available
    changed_file = ""
    try:
        raw_stdin = sys.stdin.read()
        if raw_stdin.strip():
            payload = json.loads(raw_stdin)
            # Try to extract changed file from common hook payloads
            if isinstance(payload, dict):
                tool_call = payload.get("toolCall", {})
                args = tool_call.get("args", {}) if isinstance(tool_call, dict) else {}
                changed_file = (
                    args.get("TargetFile")
                    or args.get("AbsolutePath")
                    or args.get("file_path")
                    or args.get("path")
                    or payload.get("filePath")
                    or payload.get("file")
                    or ""
                )
    except Exception:
        pass

    target_skills: set[str] | None = None
    if changed_file:
        norm = changed_file.replace("\\", "/")
        if "/skills/" in norm or norm.startswith("skills/"):
            parts = norm.split("skills/")
            if len(parts) > 1:
                skill_sub = parts[1].split("/")[0]
                if skill_sub:
                    target_skills = {skill_sub}
        else:
            # Not a skill file edit, silent clean exit
            print(json.dumps({}))
            return

    # Execute sync silently or output to stderr for diagnostics
    _, summary = run_sync(repo_root, target_skills=target_skills, dry_run=False, verbose=False)
    
    if summary.get("applied_changes", 0) > 0 or summary.get("lockfile_updates"):
        print(f"[melech hook] Synced {summary['applied_changes']} files across {len(summary['results'])} local targets for skill(s): {target_skills or 'all'}", file=sys.stderr)

    # Standard hook output contract
    print(json.dumps({}))


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync local skill changes across local repos and global agent directories.")
    parser.add_argument("--check", "--dry-run", action="store_true", help="Check for deviations and outdated installs without modifying (exits 1 if deviations found).")
    parser.add_argument("--apply", "--sync", action="store_true", help="Apply updates to all found installations (default).")
    parser.add_argument("--skill", type=str, help="Sync only a specific skill by name.")
    parser.add_argument("--file", type=str, help="Infer skill from modified file path.")
    parser.add_argument("--hook", action="store_true", help="Run in agent lifecycle hook mode (JSON stdin/stdout).")
    parser.add_argument("--json", action="store_true", help="Output summary as JSON.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed file-level changes.")
    parser.add_argument("--dev-roots", type=str, help="Additional root directories to scan (comma or colon separated).")

    args = parser.parse_args()
    repo_root = find_repo_root()

    if args.hook:
        handle_hook_mode(repo_root)
        return

    extra_roots = []
    if args.dev_roots:
        for r in args.dev_roots.replace(",", ":").split(":"):
            if r.strip():
                extra_roots.append(Path(r.strip()).expanduser().resolve())

    target_skills: set[str] | None = None
    if args.skill:
        target_skills = {args.skill.strip()}
    elif args.file:
        norm = args.file.replace("\\", "/")
        if "/skills/" in norm or norm.startswith("skills/"):
            parts = norm.split("skills/")
            if len(parts) > 1:
                skill_sub = parts[1].split("/")[0]
                if skill_sub:
                    target_skills = {skill_sub}

    dry_run = args.check and not args.apply
    code, summary = run_sync(
        repo_root,
        target_skills=target_skills,
        dry_run=dry_run,
        verbose=args.verbose,
        extra_roots=extra_roots,
    )

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_report(summary, dry_run=dry_run, verbose=args.verbose)

    sys.exit(code)


if __name__ == "__main__":
    main()
