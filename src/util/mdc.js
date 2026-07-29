export function wrapAsMdc({ description, body }) {
  const frontmatter = [
    "---",
    `description: ${yamlEscape(description)}`,
    "alwaysApply: true",
    "---",
    "",
  ].join("\n");
  return `${frontmatter}${body.trim()}\n`;
}

function yamlEscape(s) {
  if (/[:#\-\[\]\{\}&*!|>'"%@`,?]/.test(s) || s.includes("\n")) {
    return `"${s.replace(/"/g, '\\"')}"`;
  }
  return s;
}
