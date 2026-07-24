# OPENCODE MEMORY DIRECTIVE

## 1. PRE-TASK RECALL BEFORE SEARCHING
- CRITICAL RULE Before using `grep`, searching the codebase, or writing any code, you MUST first read `memory/functions.md`.
- Use this file to understand the architecture, locate file connections, and find exact function names based on the user's prompt.
- Only search the actual codebase if the answer is not in the memory file.

## 2. POST-TASK AUTO-SAVE NEW SOLUTIONS
- Every time you solve a new problem, create a function, or change how files connect, you MUST automatically append the details to `memory/functions.md`.
- Do not ask the user for permission. Just do it at the end of your response.

## 3. RESPECT .GITIGNORE BEFORE SCANNING
- Before ANY file-tree scan, first read `.gitignore` from the project root.
- Exclude all paths/patterns listed in `.gitignore` from scans. Do not list or traverse them.
- This prevents scanning node_modules, .next, dist, build, .env, etc.

## 4. REPOSITORY MAP (AUTO-MAINTAIN)
- On first project exploration, save a file tree at the top of `memory/functions.md` under `## Repository Map`.
- Show individual files within every directory (expand fully).
- Exclude all `.gitignore`-matched paths.
- When creating a new file, append it. When deleting, remove it.
- At end of each session, re-scan the project and compact the map.

## 5. MEMORY LOGGING FORMAT (FILE-GROUPED)
- Group entries by file path, not by feature name.

### [relative/file/path]
 Keywords [3-5 file-level keywords]
 
 Function Names
   `functionName()`
     Keywords [2-4 per-function keywords]
     Description: [one-line what it does]

## 6. COMMENT-FIRST CODING
- When creating or editing any function, write a brief `//` comment above it.
- Format: `// functionName() - what it does`
- Enables grep fallback when memory lookup misses.

## 6b. SMART READ ON RE-READ
- When re-reading a file you have already inspected, ALWAYS use the `smart_read` tool instead of `read` to save tokens.
- Use `read` only for the first read of any file.
- `smart_read` caches content and returns only the diff on subsequent reads, avoiding redundant context.

## 6c. SEMANTIC CHUNK FOR LARGE FILES
- For files over ~300 lines, use `semantic_chunk` to get a tree of functions/classes/methods before reading specific sections.
- This lets you target only the relevant chunk instead of the whole file.

## 6d. SEMANTIC DIFF FOR STRUCTURAL CHANGES
- When comparing file versions, use `semantic_diff` instead of raw git diff to see added/removed/modified symbols by name.

## 7. AUTO-DEBUG TRIGGER
- If you catch yourself re-reading the same files, repeating the same tool calls, or circling the same logic without making progress → STOP and debug.
- Insert `console.log('DEBUG:' + JSON.stringify(...))` at suspected failure points.
- Run, read logs, identify problem, fix, remove logs.
- For crashes (no output): add try/catch + console.error at entry points.

## 8. MODULARITY RULE
- Keep each source file under ~600 lines.
- If a file exceeds this, split it.
- Each file should be independently fixable — minimize cross-file deps.

## 9. LONG TOOL CALLS — USER RUNS MANUALLY
- Commands like `pnpm add`, `pnpm build`, `pnpm install`, or any long-running setup are flagged in instructions.
- Do NOT execute them — tell the user what to run and wait.
- Always use `pnpm` (npm is deprecated).

## 10. OUTPUT COMPRESSION — PONYTAIL STYLE
- Before writing any code, question whether the feature needs to exist.
- If the native language/browser/stdlib already does it, use that — don't install a package.
- If it can be written in 1 line, don't write 50.
- Prefer concise implementations: short functions, no unnecessary abstraction.
- This is NOT a license to skip error handling — just don't add layers that don't solve a real problem.

## 11. GIT BRANCH DISCIPLINE — MAIN ONLY, NO MASTER
- Always push to `main`. Never commit or push to `master`.
- Before implementing a new feature, ask the user: "Should I create a feature branch for this?"
  - If yes: create `feature/<short-description>` and work there.
  - If no: commit directly to `main`.
- Feature branches are disposable — if code becomes unfixable, the branch can be destroyed with zero risk to `main`.
- On feature completion with user approval, merge to `main` and delete the feature branch.
