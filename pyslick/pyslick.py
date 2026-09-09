#!/usr/bin/env python3
"""
pyslick — Super Python program consolidating all PySlick tools
Usage:
    pyslick --help
    pyslick <command> --help
"""

import sys
import os
import subprocess
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Get the directory where this script is located
PYSLICK_DIR = os.path.dirname(os.path.abspath(__file__))

# Add to path for imports
sys.path.insert(0, PYSLICK_DIR)

# Dynamic imports to avoid blocking at startup
def import_find_nearest_nodes():
    from find_nearest_nodes import main as find_nearest_nodes_main
    return find_nearest_nodes_main

def import_find_stray_symbols():
    from find_stray_symbols import main as find_stray_symbols_main
    return find_stray_symbols_main

def import_gemini_query():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gemini_code", os.path.join(PYSLICK_DIR, "gemini-code-1788961689442.py"))
    gemini_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gemini_module)
    return gemini_module.query

def import_graphify_query():
    from graphify import query as graphify_query, query_json, map_symbols
    return graphify_query, query_json, map_symbols

def import_graphify_sitter():
    from graphify_sitter import main as graphify_sitter_main
    return graphify_sitter_main

def import_indentation():
    from indentation import analyze_indentation_scopes
    return analyze_indentation_scopes

def import_jsx_check():
    from jsx_tag_checker import check_jsx_tags
    return check_jsx_tags

def import_patchit():
    from patchit import main as patchit_main
    return patchit_main

def print_help():
    """Print comprehensive help listing all commands."""
    help_text = """
PySlick — Super Python Program for Code Analysis and Editing

Usage:
    pyslick <command> [args]

Commands:
    find-nearest-nodes <query>
        Fuzzy and semantic search for nodes in graphify output
        Requires: graphify output in graphify-out/graph.json, sentence-transformers, rapidfuzz

    find-stray-symbols <project_root>
        Scan directory for stray JSX symbols and unmatched tags
        Targets: .tsx files recursively

    gemini-query <file_path> <question>
        Query Python file by natural language description
        Returns: matched function source + connected call-chain

    graphify-query <file_path> <question>
        Query Python file by description with connected code
        Options: --top-k, --min-score, --depth, --direction

    graphify-sitter <user_query>
        Tree-sitter based parser for TypeScript/TSX files
        Auto-runs graphify extract if needed
        Requires: tree-sitter, tree-sitter-typescript

    indentation <file_path>
        Analyze indentation scopes and brace matching
        Detects: scope drift, stray braces, indentation mismatches
        Returns: OK message or detailed error report

    jsx-check <file_path>
        Check JSX/HTML tag matching in files
        Handles: void tags, fragments, TypeScript generics

    patchit <file> [options]
        Local agentic file editor with git-style diff
        Options: -l (show lines), -f (find replace), -d (patch), -r (range), -i (insert)

Examples:
    pyslick find-nearest-nodes "parse data"
    pyslick find-stray-symbols ./src
    pyslick gemini-query myfile.py "how does parsing work"
    pyslick graphify-query myfile.py "extract file"
    pyslick graphify-sitter "src/app/layout.tsx RootLayout"
    pyslick indentation myfile.py
    pyslick jsx-check myfile.tsx
    pyslick patchit myfile.py -l
"""
    print(help_text)

def main():
    """Main entry point for pyslick super program."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    try:
        if command == "--help" or command == "-h":
            print_help()
        elif command == "find-nearest-nodes":
            if not args:
                print("Error: find-nearest-nodes requires <query>")
                sys.exit(1)
            try:
                find_nearest_nodes_main = import_find_nearest_nodes()
                sys.argv = ["find_nearest_nodes"] + args
                find_nearest_nodes_main()
            except Exception as e:
                print(f"Error: {e}")
                print("Note: This command requires graphify output in graphify-out/graph.json")
                print("Run 'graphify extract .' first to generate the graph output.")
                sys.exit(1)
        elif command == "find-stray-symbols":
            if len(args) < 1:
                print("Error: find-stray-symbols requires <project_root>")
                sys.exit(1)
            try:
                find_stray_symbols_main = import_find_stray_symbols()
                find_stray_symbols_main(args[0])
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        elif command == "gemini-query":
            if len(args) < 2:
                print("Error: gemini-query requires <file_path> <question>")
                sys.exit(1)
            try:
                gemini_query = import_gemini_query()
                results = gemini_query(args[0], " ".join(args[1:]))
                for r in results:
                    print(r)
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        elif command == "graphify-query":
            if len(args) < 2:
                print("Error: graphify-query requires <file_path> <question>")
                sys.exit(1)
            try:
                graphify_query = import_graphify_query()[0]
                results = graphify_query(args[0], " ".join(args[1:]))
                for r in results:
                    print(r)
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        elif command == "graphify-sitter":
            if not args:
                print("Error: graphify-sitter requires <user_query>")
                sys.exit(1)
            try:
                graphify_sitter_main = import_graphify_sitter()
                graphify_sitter_main(" ".join(args))
            except Exception as e:
                print(f"Error: {e}")
                print("Note: This command requires tree-sitter and tree-sitter-typescript")
                sys.exit(1)
        elif command == "indentation":
            if len(args) < 1:
                print("Error: indentation requires <file_path>")
                sys.exit(1)
            try:
                analyze_indentation_scopes = import_indentation()
                results = analyze_indentation_scopes(args[0])
                if not results:
                    print("OK: No scope or brace mismatches detected!")
                else:
                    for err in results:
                        print(err)
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        elif command == "jsx-check":
            if len(args) < 1:
                print("Error: jsx-check requires <file_path>")
                sys.exit(1)
            try:
                check_jsx_tags = import_jsx_check()
                check_jsx_tags(args[0])
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        elif command == "patchit":
            try:
                patchit_main = import_patchit()
                sys.argv = ["patchit"] + args
                patchit_main()
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            print_help()
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
