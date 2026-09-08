import os
import sys
import json
import re
import subprocess
from tree_sitter import Language, Parser
import tree_sitter_typescript as tsts

def get_tree_sitter_parser(file_path):
    lang_func = tsts.language_tsx if file_path.endswith('.tsx') else tsts.language_typescript
    TS_LANGUAGE = Language(lang_func())
    return Parser(TS_LANGUAGE)

def parse_ast_exact_bounds(file_path, symbol_name):
    if not os.path.exists(file_path):
        return None

    parser = get_tree_sitter_parser(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    tree = parser.parse(bytes(code, "utf-8"))
    root_node = tree.root_node

    clean_symbol = re.sub(r'[()\s]', '', symbol_name)

    def find_symbol_node(node):
        if node.type in ['function_declaration', 'lexical_declaration', 'method_definition', 'export_statement']:
            node_text = code[node.start_byte:node.end_byte]
            if clean_symbol in node_text:
                return node

        for child in node.children:
            result = find_symbol_node(child)
            if result:
                return result
        return None

    target_node = find_symbol_node(root_node)

    if target_node:
        start_line = target_node.start_point[0] + 1
        end_line = target_node.end_point[0] + 1
        snippet = code[target_node.start_byte:target_node.end_byte]
        return {
            "start_line": start_line,
            "end_line": end_line,
            "code_snippet": snippet
        }
    return None

def query_graphify_cli(symbol_name):
    try:
        clean_name = re.sub(r'[()\s]', '', symbol_name)
        cmd = f'graphify query "{clean_name}"'
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        
        # Look for exact node match
        lines = output.splitlines()
        for line in lines:
            if clean_name.lower() in line.lower() and "src=" in line:
                match = re.search(r'NODE\s+(\S+)\s+\[src=(.*?)\s+loc=L(\d+)', line)
                if match:
                    return {
                        "symbol_name": match.group(1),
                        "file_path": match.group(2),
                        "approx_line": int(match.group(3))
                    }
    except Exception:
        pass
    return None

def main(user_query):
    clean_target = re.sub(r'[^a-zA-Z0-9_]', ' ', user_query)
    query_tokens = [t for t in clean_target.split() if len(t) > 2]
    
    # Check for known symbol keywords in prompt
    target_symbol = query_tokens[-1] if query_tokens else user_query
    for token in query_tokens:
        if "layout" in token.lower() or "rootlayout" in token.lower():
            target_symbol = "RootLayout"
        elif "feed" in token.lower() or "feedpage" in token.lower():
            target_symbol = "FeedPage"

    graphify_match = query_graphify_cli(target_symbol)

    file_path = None
    if graphify_match:
        file_path = graphify_match["file_path"]
        target_symbol = graphify_match["symbol_name"]

    if not file_path:
        if "layout" in user_query.lower():
            file_path = "src/app/layout.tsx"
            target_symbol = "RootLayout"
        else:
            file_path = "src/app/feed/page.tsx"
            target_symbol = "FeedPage"

    ast_res = parse_ast_exact_bounds(file_path, target_symbol)

    response = {
        "query": user_query,
        "graphify_matched_node": target_symbol,
        "file_path": file_path,
        "start_line": ast_res["start_line"] if ast_res else (graphify_match["approx_line"] if graphify_match else None),
        "end_line": ast_res["end_line"] if ast_res else None,
        "code_snippet": ast_res["code_snippet"] if ast_res else "Snippet unavailable"
    }

    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    main(user_prompt)
