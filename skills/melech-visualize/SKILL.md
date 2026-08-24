---
name: melech-visualize
description: Turn an idea, flow, or structure into a compact ASCII diagram.
disable-model-invocation: true
---

# Visualize

Take the current chat context and render the relevant idea in compact ASCII.

Draw the thing that would make the discussion click:
a flow, structure, screen, sequence, boundary, comparison, or current mental model.

Keep it simple, readable, and practical.
Prefer the smallest diagram that clarifies the point.

Use clear labels and arrows.
Make reasonable assumptions when needed, but mark them.
Separate confirmed details from inferred ones.
If the drawing exposes a cleaner shape, awkward flow, or missing piece, say so briefly.

Ask very few clarifying questions.
If enough context exists, start drawing directly.

After the diagram, briefly explain:
- what it shows
- what assumptions were made
- what became clearer
- and any important ambiguity still open


## Example interactions

### 1) Backend flow

**User**
```text
melech-visualize how project creation works end to end
```

**Assistant**

```text
Homepage submit → create-project workflow

  HomepagePromptInput
        |
        v
  POST /api/v1/workflows/create-project
        |
        v
  WorkflowsController.createProject()
        |
        +---> WorkspaceService.getOrCreateDefault(user)
        |
        +---> ProjectService.create(dto)
        |       |
        |       +---> AuthService.createSubTenant()
        |       +---> AuthService.assignUserToTenant(PROJECT_ADMIN)
        |       +---> ProjectRepository.save()  → INSERT projects
        |       +---> AnalyticsService.track()
        |       +---> EventPublisher → message bus
        |
        v
  Response { workspaceId, projectId }
        |
        v
  Navigate to /editor/{projectId}

What it shows:
- auth tenant isolation happens at creation time, not lazily
- bus events fan out to quota-service, thumbnail-service

Assumptions:
- Auth calls succeed (no retry shown)

What became clearer:
- project creation has side effects across 3 external systems (auth, message bus, analytics)
- a failure after DB insert but before tenant assignment leaves a broken project
```

### 2) UI layout — adding a feature to homepage

**User**

```text
melech-visualize a "recently viewed" section on the homepage
```

**Assistant**

```text
Current homepage layout (web-app/src/routes/index.tsx)

+--------------------------------------------------+
| Topbar                                           |
+--------------------------------------------------+
| Hero (title, subtitle, gradient bg)              |
+--------------------------------------------------+
| HomePagePromptInput                              |
| [Suggestions chips]                              |
+--------------------------------------------------+
| ProjectList                                      |
|  [Filters: all | published | draft]  [Search]    |
|  +------------+ +------------+ +------------+    |
|  | ProjectCard| | ProjectCard| | ProjectCard|    |
|  +------------+ +------------+ +------------+    |
+--------------------------------------------------+

With "recently viewed" added

+--------------------------------------------------+
| Topbar                                           |
+--------------------------------------------------+
| Hero (title, subtitle, gradient bg)              |
+--------------------------------------------------+
| HomePagePromptInput                              |
| [Suggestions chips]                              |
+--------------------------------------------------+
| RecentlyViewed              ← NEW                |
|  +--------+ +--------+ +--------+ +--------+    |
|  | thumb  | | thumb  | | thumb  | | thumb  |    |
|  | name   | | name   | | name   | | name   |    |
|  +--------+ +--------+ +--------+ +--------+    |
+--------------------------------------------------+
| ProjectList                                      |
|  [Filters: all | published | draft]  [Search]    |
|  +------------+ +------------+ +------------+    |
|  | ProjectCard| | ProjectCard| | ProjectCard|    |
|  +------------+ +------------+ +------------+    |
+--------------------------------------------------+

What it shows:
- recently viewed sits between prompt and full project list
- horizontal scroll row, compact cards (no filters/search needed)

Assumptions:
- "recently viewed" is per-user, stored server-side (not localStorage)
- max ~10 items, horizontal overflow

What became clearer:
- needs a new API endpoint (GET /projects/recent) or query param on existing
- ProjectCard may need a compact variant, or this uses a separate simpler component
- if list is empty (new user), section should hide entirely
```

### 3) Service-to-service architecture

**User**

```text
melech-visualize how publish/deploy works across services
```

**Assistant**

```text
Publish flow across microservices

  web-app                     api-service               deploy-orchestrator
  +-----------+              +----------------+         +------------------+
  | Editor UI |--publish-->  | ProjectService |         |                  |
  +-----------+              |  .publish()    |         |                  |
                             +-------+--------+         |                  |
                                     |                  |                  |
                      DeploymentClientService           |                  |
                        .triggerDeployment() ---------> | workflow engine  |
                                     |                  |   starts         |
                                     v                  +--------+---------+
                             ProjectRepository                   |
                              update deployment                  |
                              metadata                           v
                                                         EdgeDeployModule
                                                          - DNS setup
                                                          - edge deploy
                                                                 |
                                                                 v
                                                         sandbox-proxy
                                                          - runtime ready
                                                          - health check

What it shows:
- api-service triggers but doesn't wait for full deploy
- workflow engine orchestrates the multi-step deploy (DNS, edge, runtime)
- deployment is async — editor polls for status

Assumptions:
- workflow engine handles retries/failures internally
- EdgeDeployModule covers both DNS and worker deployment

What became clearer:
- three separate systems need to succeed for a publish (workflow engine, edge deploy, sandbox runtime)
- rollback story is unclear — what happens if DNS succeeds but runtime fails?
```

### 4) Compare two approaches

**User**

```text
melech-visualize adding project search as a new endpoint vs query param on existing
```

**Assistant**

```text
Option A: New endpoint GET /api/v1/projects/search?q=term

  ProjectController                ProjectService
  +------------------+            +------------------+
  | @Get('/search')  |----------->| searchProjects() |
  | query: { q }     |            | new repo method  |
  +------------------+            +------------------+
                                         |
                                  ProjectRepository
                                   .createQueryBuilder()
                                   .where("name ILIKE :q")

Option B: Query param on existing GET /api/v1/projects?search=term

  ProjectController                ProjectService
  +------------------+            +------------------+
  | @Get('/')        |----------->| findAll(filters)  |
  | existing route   |            | add search param  |
  | + search param   |            | to existing query |
  +------------------+            +------------------+

What it shows:
- Option A: isolated, but duplicates pagination/filter logic
- Option B: one code path, search is just another filter

Assumptions:
- search is name-only for now, not full-text across metadata

What became clearer:
- Option B is simpler — findAll already handles workspaceId + status filters
- Option A only makes sense if search needs different response shape or permissions
```

### 5) Current mental model

**User**

```text
melech-visualize your current understanding of the chat/AI flow
```

**Assistant**

```text
Current understanding of editor chat flow

  Editor UI (web-app)
  +-------------------+
  | ChatPanel         |
  |  user sends msg   |
  +--------+----------+
           |
    POST /api/v1/chat/messages
           |
           v
  +-------------------+     +------------------+
  | ChatController    |---->| ChatService      |
  +-------------------+     |  .sendMessage()  |
                            +--------+---------+
                                     |
                          +----------+----------+
                          |                     |
                    LLM API call          ToolExecutor
                    (Claude/GPT)          (sandbox ops,
                     via agent SDK         file read/write)
                          |                     |
                          v                     v
                    chat_messages         SandboxService
                    table (parts,         → sandbox SDK
                    usage jsonb)          → file system ops

  [?] unclear: how streaming responses reach the UI
  [?] unclear: where tool results feed back into the LLM loop

What it shows:
- chat is synchronous request/response at the HTTP level
- tool execution happens server-side within the message handling

Assumptions:
- streaming uses SSE or similar (not websockets)
- tool calls loop back into the LLM for follow-up

What became clearer:
- the biggest unknown is the agent loop — single-shot or multi-turn tool use?
```
