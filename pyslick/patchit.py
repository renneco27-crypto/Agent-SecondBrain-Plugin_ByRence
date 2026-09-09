#!/usr/bin/env python3
"""
patchit.py — Local agentic file editor with git-style diff
Usage:
  python patchit.py <file>          # paste new version interactively
  python patchit.py <file> -l       # show file with line numbers
  python patchit.py <file> -d <patch_file>  # apply a .diff / .patch file
  python patchit.py <file> -r <start> <end> # delete line range
  python patchit.py <file> -i <line> # insert after line number
"""

import sys
import os
import argparse
import difflib
import shutil
from datetime import datetime

# ── color helpers ────────────────────────────────────────────────────────────
def supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

RED    = "\033[31m" if supports_color() else ""
GREEN  = "\033[32m" if supports_color() else ""
CYAN   = "\033[36m" if supports_color() else ""
YELLOW = "\033[33m" if supports_color() else ""
DIM    = "\033[2m"  if supports_color() else ""
BOLD   = "\033[1m"  if supports_color() else ""
RESET  = "\033[0m"  if supports_color() else ""

def color_diff(diff_lines):
    out = []
    for line in diff_lines:
        if line.startswith("+++") or line.startswith("---"):
            out.append(f"{BOLD}{line}{RESET}")
        elif line.startswith("@@"):
            out.append(f"{CYAN}{line}{RESET}")
        elif line.startswith("+"):
            out.append(f"{GREEN}{line}{RESET}")
        elif line.startswith("-"):
            out.append(f"{RED}{line}{RESET}")
        else:
            out.append(f"{DIM}{line}{RESET}")
    return out

# ── core diff + apply ────────────────────────────────────────────────────────
def show_diff(original: str, modified: str, filepath: str):
    a = original.splitlines(keepends=True)
    b = modified.splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        a, b,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
        lineterm=""
    ))
    if not diff:
        print(f"{YELLOW}No changes detected.{RESET}")
        return False
    print("\n" + "─" * 60)
    for line in color_diff(diff):
        print(line)
    print("─" * 60)
    # summary
    adds = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    dels = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    print(f"\n{GREEN}+{adds}{RESET}  {RED}-{dels}{RESET}  lines changed\n")
    return True

def backup(filepath: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{filepath}.bak_{ts}"
    shutil.copy2(filepath, bak)
    print(f"{DIM}Backup -> {bak}{RESET}")

def write_file(filepath: str, content: str):
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        f.write(content)

def read_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def confirm(prompt="Apply changes? [y/N] ") -> bool:
    try:
        ans = input(prompt).strip().lower()
        return ans in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        print()
        return False

# ── modes ────────────────────────────────────────────────────────────────────
def mode_show_lines(filepath: str):
    """Print file with line numbers."""
    content = read_file(filepath)
    lines = content.splitlines()
    width = len(str(len(lines)))
    for i, line in enumerate(lines, 1):
        print(f"{DIM}{str(i).rjust(width)}{RESET}  {line}")

def mode_paste(filepath: str):
    """Paste new file version interactively."""
    original = read_file(filepath)
    print(f"{BOLD}Paste the new version of {filepath}{RESET}")
    print(f"{DIM}End input with a line containing only: END{RESET}\n")
    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
    except EOFError:
        pass
    modified = "\n".join(lines)
    if not modified.endswith("\n"):
        modified += "\n"
    changed = show_diff(original, modified, filepath)
    if changed and confirm():
        backup(filepath)
        write_file(filepath, modified)
        print(f"{GREEN}✓ Applied.{RESET}")
    elif not changed:
        print("Nothing to do.")
    else:
        print(f"{YELLOW}Aborted.{RESET}")

def mode_patch_file(filepath: str, patch_path: str):
    """Apply a unified diff file using difflib."""
    try:
        import whatthepatch
        use_wtp = True
    except ImportError:
        use_wtp = False

    original = read_file(filepath)
    patch_text = read_file(patch_path)

    if use_wtp:
        # use whatthepatch for fuzzy application
        patches = list(whatthepatch.parse_patch(patch_text))
        if not patches:
            print(f"{RED}No valid patches found in {patch_path}{RESET}")
            return
        p = patches[0]
        orig_lines = original.splitlines()
        new_lines = list(whatthepatch.apply_diff(p, orig_lines))
        modified = "\n".join(new_lines) + "\n"
    else:
        # fallback: naive apply using difflib
        print(f"{YELLOW}tip: pip install whatthepatch for fuzzy patch application{RESET}")
        # just show what the patch says and let user decide
        print(patch_text)
        print(f"\n{RED}Cannot auto-apply without whatthepatch. Install it or use paste mode.{RESET}")
        return

    changed = show_diff(original, modified, filepath)
    if changed and confirm():
        backup(filepath)
        write_file(filepath, modified)
        print(f"{GREEN}✓ Applied.{RESET}")
    elif not changed:
        print("Nothing to do.")
    else:
        print(f"{YELLOW}Aborted.{RESET}")

def mode_delete_range(filepath: str, start: int, end: int):
    """Delete lines start..end (1-indexed, inclusive)."""
    original = read_file(filepath)
    lines = original.splitlines(keepends=True)
    total = len(lines)
    if start < 1 or end > total or start > end:
        print(f"{RED}Invalid range {start}-{end} (file has {total} lines){RESET}")
        return
    print(f"{YELLOW}Deleting lines {start}–{end}:{RESET}")
    for i in range(start - 1, end):
        print(f"  {RED}-{str(i+1).rjust(4)}{RESET}  {lines[i]}", end="")
    modified_lines = lines[:start-1] + lines[end:]
    modified = "".join(modified_lines)
    changed = show_diff(original, modified, filepath)
    if changed and confirm():
        backup(filepath)
        write_file(filepath, modified)
        print(f"{GREEN}✓ Applied.{RESET}")
    else:
        print(f"{YELLOW}Aborted.{RESET}")

def mode_insert(filepath: str, after_line: int):
    """Insert text after a given line number."""
    original = read_file(filepath)
    lines = original.splitlines(keepends=True)
    total = len(lines)
    if after_line < 0 or after_line > total:
        print(f"{RED}Invalid line {after_line} (file has {total} lines){RESET}")
        return
    print(f"{BOLD}Paste lines to insert after line {after_line}{RESET}")
    print(f"{DIM}End with a line containing only: END{RESET}\n")
    new_lines = []
    try:
        while True:
            line = input()
            if line.strip() == "END":
                break
            new_lines.append(line + "\n")
    except EOFError:
        pass
    modified_lines = lines[:after_line] + new_lines + lines[after_line:]
    modified = "".join(modified_lines)
    changed = show_diff(original, modified, filepath)
    if changed and confirm():
        backup(filepath)
        write_file(filepath, modified)
        print(f"{GREEN}✓ Applied.{RESET}")
    else:
        print(f"{YELLOW}Aborted.{RESET}")

def mode_find_replace(filepath: str):
    """Find a string and replace it — fuzzy, ignores leading whitespace diffs."""
    original = read_file(filepath)
    print(f"{BOLD}Find (paste the OLD block, end with END):{RESET}")
    old_lines = []
    try:
        while True:
            l = input()
            if l.strip() == "END":
                break
            old_lines.append(l)
    except EOFError:
        pass
    old_block = "\n".join(old_lines)

    # try exact first
    if old_block in original:
        print(f"\n{GREEN}✓ Exact match found.{RESET}")
    else:
        # try stripped lines match
        orig_lines = original.splitlines()
        search_lines = old_block.splitlines()
        # find first occurrence of first search line (stripped)
        match_start = None
        for i, ol in enumerate(orig_lines):
            if ol.strip() == search_lines[0].strip():
                # check rest
                if all(
                    (i + j) < len(orig_lines) and
                    orig_lines[i + j].strip() == search_lines[j].strip()
                    for j in range(len(search_lines))
                ):
                    match_start = i
                    break
        if match_start is None:
            print(f"{RED}Could not find that block in the file.{RESET}")
            print(f"{DIM}Try -l to view line numbers and use -r to delete a range.{RESET}")
            return
        # rebuild old_block from actual file lines so replace works
        old_block = "\n".join(orig_lines[match_start:match_start + len(search_lines)])
        print(f"{GREEN}✓ Fuzzy match found at line {match_start + 1}.{RESET}")

    print(f"\n{BOLD}Replace with (paste NEW block, end with END):{RESET}")
    new_lines = []
    try:
        while True:
            l = input()
            if l.strip() == "END":
                break
            new_lines.append(l)
    except EOFError:
        pass
    new_block = "\n".join(new_lines)
    modified = original.replace(old_block, new_block, 1)
    changed = show_diff(original, modified, filepath)
    if changed and confirm():
        backup(filepath)
        write_file(filepath, modified)
        print(f"{GREEN}✓ Applied.{RESET}")
    elif not changed:
        print("Nothing to do.")
    else:
        print(f"{YELLOW}Aborted.{RESET}")

# ── main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="patchit — local agentic file editor with git diff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes (pick one):
  (default)         Paste new full file version
  -l                Show file with line numbers
  -f                Find & replace block (fuzzy)
  -d <patch>        Apply a .diff/.patch file
  -r <start> <end>  Delete line range (1-indexed)
  -i <line>         Insert text after line number
        """
    )
    parser.add_argument("file", help="File to edit")
    parser.add_argument("-l", "--lines",  action="store_true", help="Show with line numbers")
    parser.add_argument("-f", "--find",   action="store_true", help="Find & replace mode")
    parser.add_argument("-d", "--diff",   metavar="PATCH",     help="Apply .diff file")
    parser.add_argument("-r", "--range",  nargs=2, metavar=("START","END"), type=int, help="Delete line range")
    parser.add_argument("-i", "--insert", metavar="LINE",      type=int, help="Insert after line N")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"{RED}File not found: {args.file}{RESET}")
        sys.exit(1)

    print(f"{BOLD}patchit{RESET} -> {CYAN}{args.file}{RESET}")

    if args.lines:
        mode_show_lines(args.file)
    elif args.find:
        mode_find_replace(args.file)
    elif args.diff:
        mode_patch_file(args.file, args.diff)
    elif args.range:
        mode_delete_range(args.file, args.range[0], args.range[1])
    elif args.insert:
        mode_insert(args.file, args.insert)
    else:
        mode_paste(args.file)

if __name__ == "__main__":
    main()
