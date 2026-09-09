# AI coding agent — universal workflow guide
## Tools: graphify · tree-sitter · pyslick · PowerShell · git

This is a prompt for an AI coding agent. Follow it exactly.
When a step returns ❌ or an error — STOP. Do not proceed.
Copy the full terminal output and send it to the AI before continuing.

---

## Setting up graphify (do this first, on every new machine or project)

Graphify is the tool that lets an AI actually understand your codebase — which file a symbol lives in, how components connect, what breaks if you change X. Without it, the AI is guessing.

### Step 1 — Install graphify globally

```powershell
npm install -g graphify-code
```

Verify it installed:

```powershell
graphify --help
```

You should see the full command list. If you get "command not found", close and reopen PowerShell.

### Step 2 — Go to your project folder

```powershell
cd "C:\Users\yourname\Documents\projects\myproject"
```

Always run graphify from the root of your project (same folder as `package.json`).

### Step 3 — Index your codebase

If you have an Anthropic/OpenAI/Gemini API key (recommended — gives richer docs):

```powershell
graphify extract .
```

If you don't have an API key, code-only mode still gives the AI full structural understanding:

```powershell
graphify extract . --code-only
```

This builds `graphify-out/graph.json` — the map of your entire codebase. Takes 30 seconds to a few minutes depending on project size.

### Step 4 — Register graphify with Claude (or your AI)

```powershell
graphify claude install
```

This writes a `CLAUDE.md` file at your project root that Claude reads automatically at the start of every session. It tells Claude how to use graphify to look up your code before touching anything.

For other AI tools, use the matching install command:

```powershell
graphify cursor install      # Cursor
graphify codex install       # Codex / AGENTS.md
graphify opencode install    # OpenCode
graphify kiro install        # Kiro IDE
```

### Step 5 — Verify the graph works with a test query

```powershell
graphify query "what does this project do"
graphify query "find all usages of Sidebar"
graphify query "how does auth connect to the dashboard"
```

If those return meaningful answers, graphify is working. The AI can now use the same queries to look up any symbol before editing it.

### Step 6 — Keep the graph updated after big changes

After adding new files, renaming components, or major refactors:

```powershell
# Re-index changed code files only (fast, no API key needed)
graphify update .

# Full re-extract if the structure changed a lot
graphify extract . --code-only --force
```

> `--force` is needed after deleting files or renaming components — without it, graphify keeps stale nodes.

### Graphify quick reference

| What you want | Command |
|---|---|
| Index a new project | `graphify extract . --code-only` |
| Register with Claude | `graphify claude install` |
| Ask about the codebase | `graphify query "your question"` |
| Find which file a symbol is in | `graphify query "where is ComponentName defined"` |
| See what a component connects to | `graphify explain "ComponentName"` |
| Find what breaks if you change X | `graphify affected "ComponentName"` |
| See the most connected files | `graphify god-nodes` |
| Update after code changes | `graphify update .` |
| Force full re-index | `graphify extract . --force` |
| View graph visually in browser | Open `graphify-out/graph.html` |

---

## How to use AI for coding — general workflow

Working with an AI coding agent effectively means treating it like a very fast junior dev who cannot see your screen. Your job is to give it exact context; its job is to give you exact commands to run.

### The golden rules

1. **Never let the AI guess line numbers.** Always read the file first and share the output.
2. **One change at a time.** Make an edit, verify, then move to the next.
3. **Always save a checkpoint** (git stash or commit) before any edit. One command reverts everything.
4. **When something breaks, stop and send the full error.** Don't try to fix errors by continuing — paste the terminal output to the AI.
5. **The build is ground truth.** `pnpm build` (or your equivalent) passing = change is safe. Passing linters but failing build = not done.

### Step-by-step: how to run an AI coding session

**Before you start:**
```
1. Open your project in the terminal
2. Run: git stash   ← safety net before anything
3. Tell the AI what you want to change (be specific — name the component/file/behaviour)
```

**During the session:**
```
1. AI gives you a command → run it exactly, paste the full output back
2. AI makes an edit → run pyslick/build to verify before moving on
3. Something looks wrong → STOP, paste the error, wait for AI to fix it
4. Change works → git commit -m "checkpoint: <what you did>"
```

**When it breaks:**
```
1. Do NOT keep running more commands hoping it fixes itself
2. Paste the full terminal error to the AI
3. If the AI cannot fix it in 2 tries → git reset --hard HEAD  (back to last checkpoint)
4. Start fresh with a cleaner description of what you wanted
```

### What to tell the AI at the start of a session

Always provide:
- What file or component you want to change (exact path if you know it)
- What it currently does vs what you want it to do
- Any error message you're already seeing
- Your stack (Next.js, React, etc.) if it's not obvious

Example prompt:
> "I want to change the logo in `src/components/Sidebar.tsx`. Currently it shows a text wordmark. I want it to show `public/icon-192.png` instead. Stack is Next.js App Router + TypeScript."

### How to hand off to the next AI session

At the end of a session, ask the AI:
> "Summarize what we did, what state the codebase is in, and what the next step is — so I can paste this into a new session."

Always include in the handoff:
- Last commit hash (`git log --oneline -3`)
- What was changed and why
- What still needs to be done
- Any known issues or workarounds in place

---

## The core principle

Never edit a file by guessing line numbers or searching raw text.
Always locate the exact symbol bounds first via tree-sitter, then replace only within those lines.
Always verify with pyslick after every edit. Always build before committing.

---

## Tools available

| Tool | What it does |
|---|---|
| `graphify query` | Find which file/community a symbol lives in |
| `graphify_sitter.py` | Get exact AST start_line and end_line for a symbol |
| `Get-Content` / `cat` | Read file contents before touching anything |
| `pyslick/indentation.py` | Catch stray braces and scope drift after edits |
| `pyslick/jsx_tag_checker.py` | Catch mismatched JSX tags after edits |
| `Invoke-SitterReplace` | Replace only within AST bounds (if loaded in session) |
| `git` | Save points, diffs, rollbacks |
| `pnpm build` | Final verification before deploy |

---

## Step 0 — Read the file before touching it

Always cat the target file first. Never edit blind.

```powershell
# Normal path
Get-Content "src/app/layout.tsx"

# Path with [brackets] — always use -LiteralPath
Get-Content -LiteralPath "src/app/study/[deckId]/page.tsx" | Select-Object -First 40
```

> ⚠️ If output shows ❌ or "does not exist" — STOP. Send to AI.

---

## Step 1 — Save point before any edit

```powershell
# Option A — stash
git stash

# Option B — commit
git add .
git commit -m "checkpoint before edit"
```

Roll back instantly if anything breaks:

```powershell
git reset --hard HEAD
# or to a specific commit
git reset --hard <commit-hash>
```

> ⚠️ Never skip this step. One command rollback saves everything.

---

## Step 2 — Find the symbol with graphify

Confirm the symbol exists and which file it lives in.

```powershell
graphify query "describe <SymbolName> in <filename>"
```

Check output for:
- `file_path` — correct file
- `community` — confirms it's part of the right module cluster
- `loc` — approximate line for sanity check

> ⚠️ If graphify returns wrong file or no match — STOP. Send to AI.
> ⚠️ If graphify returns a non-.tsx/.ts file (e.g. components.json) — it matched wrong. Use tree-sitter with an explicit path instead (see Step 3).
> ⚠️ If graphify returns "No matching nodes found" — the symbol does not exist yet. Do not proceed with an import or usage. Either create the component first or remove the reference.

---

## Step 3 — Get exact AST bounds with tree-sitter

Always use the explicit full path format. Bare filenames cause sitter to match wrong files (e.g. components.json).

```powershell
# ✅ Correct — always include full src/ path
python graphify_sitter.py "find <SymbolName> in src/path/to/File.tsx"

# ❌ Wrong — bare filename causes wrong file match
python graphify_sitter.py "find <SymbolName> in File.tsx"
```

Expected output:

```json
{
  "file_path": "src/components/AuthGate.tsx",
  "start_line": 8,
  "end_line": 154,
  "code_snippet": "export default function AuthGate() { ... }"
}
```

Verify before continuing:
- `file_path` is a `.tsx` or `.ts` file — not `components.json` or similar
- `start_line` and `end_line` are not null
- `code_snippet` starts at the function/component definition
- `code_snippet` ends at the closing `}`

> ⚠️ If file_path is not a .tsx/.ts — sitter matched wrong. Add full explicit src/ path to your query.
> ⚠️ If start_line/end_line are null — sitter could not find the symbol. Get line count and overwrite the whole file instead (see Step 5 fallback).
> ⚠️ If bounds look wrong or snippet is truncated — STOP. Send to AI.

### Get line count when sitter fails

```powershell
Get-Content -LiteralPath "src/components/File.tsx" | Measure-Object -Line
```

Use this to know the full file length for array slicing or full overwrite.

---

## Step 4 — Write replacement using single-quote here-string

Use `@' '` (single-quote) for any code containing JSX, `${}`, or template literals.
Never use `@" "` — PowerShell will expand `${}` as variables and corrupt JSX.

```powershell
$newCode = @'
export default function MyComponent() {
  return (
    <div className={`${someVar} other-class`}>
      content
    </div>
  )
}
'@
```

---

## Step 5 — Replace within AST bounds

### If Invoke-SitterReplace is loaded in session:

```powershell
Invoke-SitterReplace -Query "find <SymbolName> in src/path/to/File.tsx" -NewCode $newCode
```

### If Invoke-SitterReplace is NOT available (fallback — array slicing):

Use the exact line numbers from Step 3. Arrays are zero-based — line 43 = index 42.

```powershell
$filePath = "src/app/layout.tsx"
$lines = Get-Content $filePath
$newLines = $newCode -split "`n"

# start_line=43, end_line=79 → indices 0..41 (before) and 79.. (after)
$lines = $lines[0..41] + $newLines + $lines[79..($lines.Length - 1)]
Set-Content $filePath $lines -Encoding UTF8
```

### If sitter fails entirely (fallback — full file overwrite):

When sitter returns null bounds, overwrite the whole file using `Set-Content` with a here-string.
Always use single-quote `@' '` to prevent PowerShell from expanding JSX expressions.

```powershell
$newCode = @'
<entire file contents here>
'@
Set-Content -LiteralPath "src/components/File.tsx" $newCode -Encoding UTF8
```

> ⚠️ After running — immediately verify with pyslick before anything else.

---

## Step 6 — Verify with pyslick immediately after edit

Run both checkers on every file you touched:

```powershell
python "C:\Users\corte\Documents\do not delete second brain\pyslick\indentation.py" "<path-to-file>"
python "C:\Users\corte\Documents\do not delete second brain\pyslick\jsx_tag_checker.py" "<path-to-file>"
```

Expected output: `✅ No scope or brace mismatches detected!`

> ⚠️ If output shows ❌ — STOP. Do not proceed to the next step.
> Copy the full error line and send it to the AI.
> Fix using array index slicing (see debugging section), then re-run pyslick.

### Known pyslick false positives — safe to ignore, trust the build instead

These patterns cause pyslick to report errors that are not real:

| Pattern | Why it false-positives |
|---|---|
| `<html lang="en" className={...}>` | Dynamic attributes with `[` or `{` confuse tag regex |
| Inline `<svg>` with `<path d="...">` | SVG path `d=` attributes contain `>` characters |
| Multi-line JSX tags `<form\n  onSubmit=...` | Tag opens on one line, `>` closes on another |

When pyslick reports ❌ on these patterns and the file looks structurally correct — run `pnpm build` directly. A passing build is the ground truth.

---

## Step 7 — Add imports after the replacement

Imports live outside symbol bounds. Always add them after the replacement is done
to avoid shifting line numbers before sitter runs.

```powershell
$filePath = "src/app/layout.tsx"
$content = Get-Content $filePath -Raw

if ($content -notmatch "import NewComponent") {
    $content = $content -replace "import ExistingImport from 'somewhere'", "import ExistingImport from 'somewhere'`r`nimport NewComponent from '@/components/NewComponent'"
    Set-Content $filePath $content -Encoding UTF8
    Write-Host "Added import" -ForegroundColor Green
}
```

> ⚠️ In Next.js App Router files with `'use client'`: that directive MUST be
> line 1. Insert imports after it, never before.

---

## Step 8 — Verify the diff

```powershell
git diff <filepath>
```

Check:
- Only intended lines changed
- No surrounding code corrupted
- No extra blank lines or indentation drift
- All existing providers/wrappers still present

> ⚠️ If diff shows unexpected changes outside your target lines — STOP. Send to AI.

---

## Step 9 — Build

```powershell
pnpm build
```

✅ Build passes → commit and deploy.
❌ Build fails → go to the debugging section below. Do not commit.

Roll back if needed:

```powershell
git reset --hard HEAD
```

---

## Step 10 — Commit and deploy

```powershell
git add .
git commit -m "feat: describe what you changed"
git push origin <branch-name>
```

If remote is ahead (non-fast-forward rejection):

```powershell
git push origin <branch-name> --force
```

---

## Step 11 — Verify the live site by code

After deploy, scan the server-rendered root route to confirm changes are live:

```powershell
$response = Invoke-WebRequest -Uri "https://your-site.onrender.com/" -UseBasicParsing
if ($response.Content -match "thing-you-added") {
    Write-Host "✅ Live and active" -ForegroundColor Green
} else {
    Write-Host "❌ Not found in response" -ForegroundColor Red
}
```

> Scan `/` not a client-rendered route. Client routes return minimal HTML
> since they render in the browser, not on the server.

---

## Cheat sheet — order of operations

```
cat the file first              ← never edit blind
git stash / commit              ← save point
graphify query                  ← confirm symbol exists and file
  → "No matching nodes" = symbol doesn't exist, stop
  → non-.tsx result = matched wrong, use explicit path in sitter
graphify_sitter.py              ← always use full src/ path
  → null bounds = sitter failed, get line count + full overwrite
write $newCode with @' '        ← single-quote, no PS interpolation
Invoke-SitterReplace            ← replace only within AST bounds
  → if unavailable: array slice using sitter line numbers
  → if sitter failed: full file overwrite with Set-Content
pyslick indentation.py          ← ❌ = STOP, send to AI
pyslick jsx_tag_checker.py      ← ❌ = STOP, send to AI
  → known false positives: html attrs, inline SVG, multi-line tags
  → if structurally correct: trust pnpm build over pyslick
add imports after               ← outside bounds, done separately
git diff                        ← verify only intended lines changed
pnpm build                      ← ❌ = STOP, send error to AI
git commit + push               ← only after clean build
verify live site by code        ← Invoke-WebRequest scan
```

---

## Debugging build errors

When `pnpm build` fails — read the error, identify the file and line, then pick
the right fix below. Do not guess. Do not regex the whole file.

> ⚠️ At every step below: if pyslick returns ❌ — STOP. Send full output to AI.

---

### Syntax error / Expression expected / Unexpected token

Stray or duplicate `}` from a PowerShell replacement.

```powershell
python "C:\Users\corte\Documents\do not delete second brain\pyslick\indentation.py" "<file-from-error-trace>"
```

If it reports `❌ [Line N, Col 1] Stray closing '}'` — remove that exact line.
Arrays are zero-based: line 80 = index 79.

```powershell
$lines = Get-Content "<filepath>"
$lines = $lines[0..78] + $lines[80..($lines.Length - 1)]
Set-Content "<filepath>" $lines -Encoding UTF8
```

Re-run pyslick to confirm `✅` before rebuilding.

---

### Tags merged onto one line after a replace

When a regex replace removes a JSX component, the surrounding tags can collapse onto one line:

```
<ThemeProvider ...>          <ServiceWorkerRegister />
```

Fix by restoring the newline:

```powershell
$content = Get-Content -LiteralPath "<filepath>" -Raw
$content = $content -replace "<ThemeProvider attribute=`"class`"...>          <ServiceWorkerRegister />", "<ThemeProvider attribute=`"class`"...>`r`n          <ServiceWorkerRegister />"
Set-Content -LiteralPath "<filepath>" $content -Encoding UTF8
```

> ⚠️ Always read the file with `Select-Object -Last 20` after a regex remove to catch this.

---

### Duplicate identifier 'X'

Same import appears twice.

```powershell
Get-Content "<filepath>" | Select-Object -First 10
```

Find the duplicate line number, remove it by index:

```powershell
$lines = Get-Content "<filepath>"
$lines = $lines[0..<line-2>] + $lines[<line>..($lines.Length - 1)]
Set-Content "<filepath>" $lines -Encoding UTF8
```

---

### Cannot find name 'X' — missing module import

Symbol is used but not imported.

```powershell
# Read imports at top of file
Get-Content -LiteralPath "<filepath>" | Select-Object -First 40

# Confirm which module exports it
python graphify_sitter.py "find <symbolName> in src/path/to/file.tsx"
```

Add to the existing import line:

```powershell
$content = Get-Content -LiteralPath "<filepath>" -Raw
$content = $content -replace 'import \{ ExistingA, ExistingB \}', 'import { ExistingA, ExistingB, MissingSymbol }'
Set-Content -LiteralPath "<filepath>" $content -Encoding UTF8
```

> ⚠️ If graphify returns "No matching nodes" for the symbol — it does not exist in the codebase. Do not add the import. Either create the component or remove the JSX usage.

---

### Cannot find name 'X' — runtime global

Symbol is injected at runtime by a third-party wrapper (Median, OneSignal,
browser extension, etc.) — no npm package exists for it.

```powershell
$content = Get-Content "<filepath>" -Raw
$content = "declare const <symbolName>: any`r`n`r`n" + $content
Set-Content "<filepath>" $content -Encoding UTF8
```

---

### Invoke-SitterReplace not recognized

The cmdlet isn't loaded in this PowerShell session. Fall back to direct array
slicing using the line numbers from `graphify_sitter.py`:

```powershell
$lines = Get-Content "<filepath>"
$newLines = $newCode -split "`n"
$lines = $lines[0..<start_line - 2>] + $newLines + $lines[<end_line>..($lines.Length - 1)]
Set-Content "<filepath>" $lines -Encoding UTF8
```

---

## Git — handling ghost files with malformed filenames on Windows

Windows Git sometimes gets a file with a non-UTF-8 filename stuck in the local
index. It shows in `git ls-files` but cannot be removed with normal commands.

### Diagnose first

```powershell
git show origin/<branch>:<filename> 2>&1
# fatal: path does not exist → remote is clean, the ghost is local only
```

### Fix attempts in order

```powershell
# Attempt 1
git update-index --force-remove (git ls-files | Where-Object { $_ -match "filename" })

# Attempt 2 — rebuild the entire index
git rm --cached -r .
git add .
git commit -m "chore: rebuild index to remove ghost entry"
git push origin <branch> --force
```

### If it persists after remote is confirmed clean — leave it

A local-only ghost will not affect builds, deploys, CI, or anyone cloning the repo.
Confirmed clean = `git show origin/branch:file` returns `fatal: path does not exist`.

### Prevention

```powershell
Add-Content .gitignore "`ngraph.json`ngraphify-out/`n*.temp.tsx"
```

---

## Onboarding a new codebase into graphify

Works for any folder — extension, repo, script directory.

```powershell
cd C:\path\to\project

# Full extract (needs API key for docs/images)
graphify extract .

# Code-only, no key needed
graphify extract . --code-only

# Generate community names and GRAPH_REPORT.md
graphify cluster-only . --no-label

# Query
graphify query "what does this project do"
graphify query "how does X connect to Y"
graphify query "find all usages of ComponentName"

# Install as Claude context
graphify claude install
```

### Read output without opening files

```powershell
type graphify-out\GRAPH_REPORT.md
Get-Content graphify-out\GRAPH_REPORT.md | Select-Object -First 30
```

### Graphify file reference

| File | What it is |
|---|---|
| `graphify-out/graph.json` | Full graph — nodes, edges, communities |
| `graphify-out/graph.html` | Interactive visual, open in browser |
| `graphify-out/GRAPH_REPORT.md` | Human-readable community summary |
| `graphify-out/.graphify_analysis.json` | Internal analysis metadata |
| `CLAUDE.md` | AI context registered via `graphify claude install` |

### What gets skipped with `--code-only`

| File type | With key | `--code-only` |
|---|---|---|
| `.ts`, `.tsx`, `.js`, `.py` etc. | ✅ indexed | ✅ indexed |
| `.md`, `.txt`, docs | ✅ indexed | ❌ skipped |
| Images, PDFs | ✅ indexed | ❌ skipped |
| No-extension files (`.bat` etc.) | ❌ skipped | ❌ skipped |

---

## AdSense setup for Next.js

### Add ads.txt (required for approval)

```powershell
$content = "google.com, pub-XXXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0"
Set-Content -LiteralPath "public/ads.txt" $content -Encoding UTF8
```

Verify after deploy:

```powershell
Invoke-WebRequest -Uri "https://your-site.com/ads.txt" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### AdSense script in layout.tsx

Place the script in `<head>` via Next.js `<Script>` — no separate component needed:

```tsx
import Script from 'next/script'

<head>
  <Script
    async
    src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXXX"
    crossOrigin="anonymous"
    strategy="afterInteractive"
  />
</head>
```

### Enable Auto Ads (interstitials)

Go to AdSense → Ads → your site → toggle Auto ads ON.
Google handles frequency capping (once per hour per user) automatically.

### Exclude pages with dynamic segments

In AdSense → Ads → your site → Page exclusions, use wildcard patterns:

```
/study/*/flashcards
/deck/*/review
```

### Client-side auth and the AdSense crawler

If your app uses client-side auth (e.g. Supabase + `useEffect`), the AdSense crawler
sees the server-rendered HTML before JS runs — it is NOT blocked by a login wall.
The crawler can index your site normally as long as a public landing page exists at `/`.

---

## Google OAuth with Supabase

### Setup steps

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create project → APIs & Services → OAuth consent screen → External
3. APIs & Services → Credentials → Create OAuth 2.0 Client ID → Web application
4. Add authorized redirect URI:
   ```
   https://your-project.supabase.co/auth/v1/callback
   ```
5. Copy Client ID and Client Secret
6. Supabase Dashboard → Authentication → Providers → Google → paste credentials
7. Supabase → Authentication → URL Configuration → add your site URL

### Supabase OAuth button (React)

```tsx
const handleGoogle = async () => {
  const supabase = createBrowserSupabase()
  await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: window.location.origin },
  })
}
```

### Median wrapper — link handling for Google OAuth

In Median link handling rules, add at the top (before all others):

```
accounts.google.com → External Browser
*.google.com/o/oauth2/* → External Browser
```

Google blocks OAuth inside webviews. Opening in the external browser completes
auth, then deep links back into the app.

---

## PowerShell tips

```powershell
# Paste clipboard contents into terminal output
Get-Clipboard

# Right-click in PowerShell window = paste from clipboard

# Read files with brackets in path
Get-Content -LiteralPath "src/app/study/[deckId]/page.tsx"

# Read last N lines
Get-Content "file.tsx" | Select-Object -Last 5

# Read first N lines
Get-Content "file.tsx" | Select-Object -First 40

# Get total line count
Get-Content -LiteralPath "file.tsx" | Measure-Object -Line

# Find a ghost file in git index
git ls-files | Where-Object { $_ -match "filename" }

# Make sure you're in the right directory before running pyslick
cd "C:\Users\corte\Documents\projects NOT DELETE\stitchapp"
```

---

## Common mistakes and fixes

| Mistake | Fix |
|---|---|
| Used `@" "` with JSX `${}` | Switch to `@' '` |
| Added import before `'use client'` | Insert after the directive, not at line 1 |
| Added import before sitter replacement | Always replace symbol first, imports after |
| Skipped `git stash` | Always stash/commit — one command rollback |
| Ran `graphify_sitter.py` after editing | Reset file first, then re-run sitter |
| Used `-Path` for `[bracket]` folders | Use `-LiteralPath` always for those paths |
| Proceeded after pyslick ❌ | Stop immediately — send error to AI |
| Committed before build passed | Never commit on a failing build |
| Used bare filename in sitter query | Always use full `src/path/to/File.tsx` |
| Added import for non-existent symbol | Check graphify first — "No matching nodes" means create it first |
| Regex remove collapsed adjacent tags onto one line | Read last 20 lines after every regex remove |
| Ran pyslick from wrong directory | `cd` to project root before running pyslick |
| Trusted pyslick ❌ on inline SVG or multi-line tags | These are known false positives — run `pnpm build` to confirm |

---

## Git — tracing which commit broke a file (logo, layout, component)

When something visually breaks and you don't know which commit caused it:

### Step 1 — Check recent commits

```powershell
git log --oneline -20
```

### Step 2 — Search commits that touched a file by name

```powershell
git log --oneline --all --diff-filter=M -- "public/logo.jpg" "public/brand-logo.jpg"
```

For a broader keyword scan across recent commits:

```powershell
git log --oneline --all -30 | ForEach-Object {
  $hash = ($_ -split ' ')[0]
  $files = git diff-tree --no-commit-id -r --name-only $hash
  if ($files -match "logo|icon|Logo|Icon") {
    Write-Host "$_ `n$files"
  }
}
```

> Note: This finds commits touching files by name. If the logo broke due to a JSX/code change (not a file replacement), use Step 3.

### Step 3 — Inspect the exact diff of a suspect commit

```powershell
git show <commit-hash> --stat
git show <commit-hash> -- src/components/Sidebar.tsx
```

### Step 4 — Restore a single file to its pre-commit state

```powershell
git checkout <commit-hash>~1 -- src/components/Sidebar.tsx
```

### Step 5 — Restore a static asset (image) that was overwritten

Check file sizes to confirm which version is correct:

```powershell
Get-ChildItem "public" | Where-Object { $_.Name -match "icon|logo|favicon" }
```

Copy the correct file over the wrong one:

```powershell
Copy-Item -LiteralPath "public/icon-192.png" -Destination "src/app/icon.png" -Force
```

> Next.js auto-uses `src/app/icon.png` as the favicon — no metadata config needed.
> Always check file sizes when a logo looks wrong. `src/app/icon.png` (49KB original) can be silently overwritten by another image that looks similar in the file tree.

---

## Favicon in Next.js App Router

Next.js automatically uses these files as favicon/icon without any config:

| File | Used as |
|---|---|
| `src/app/icon.png` | Browser tab favicon + PWA icon |
| `src/app/favicon.ico` | Legacy favicon fallback |

To update the favicon, just replace `src/app/icon.png`:

```powershell
Copy-Item -LiteralPath "public/icon-192.png" -Destination "src/app/icon.png" -Force
Get-Item "src/app/icon.png"  # verify size matches original
```

No `metadata.icons` config needed in `layout.tsx` — file presence is enough.

---

## Google OAuth branding (Google Cloud Console)

When Google Sign-In shows the wrong app name or old logo on the consent screen:

1. Go to **Google Cloud Console → Google Auth Platform → Branding**
2. Update app name and upload new logo (must be exactly 120×120px)
3. Save — you'll see "Branding changes saved!"
4. If it says "Your branding is not being shown to users" → click **View issues**

Common blockers:
- App not verified — Google requires verification before external users see new branding
- Publishing status is "Testing" — only allowlisted test users see new branding immediately
- Logo doesn't meet size/format requirements

To check publishing status: **Google Auth Platform → Audience**
- Testing = only test users see new branding (instant)
- Production + unverified = old branding shown until Google verifies (days to weeks)
