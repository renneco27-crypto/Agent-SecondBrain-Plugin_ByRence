"""
graphify.py — Query a Python file by natural language description and retrieve
the exact matched function source code along with its full connected call-chain.
"""

import ast
import os
import re
import math
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# 1. AST Symbol & Call Extraction
# ---------------------------------------------------------------------------

def _build_parent_map(tree: ast.AST) -> dict:
    """Map each node id -> its direct AST parent node."""
    parent_map = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent_map[id(child)] = node
    return parent_map

def _extract_symbols(file_path: str, source: str, lines: list[str]) -> dict[str, dict]:
    """Parse the file and return symbol metadata including call dependencies."""
    tree = ast.parse(source, filename=file_path)
    parent_map = _build_parent_map(tree)
    symbols: dict[str, dict] = {}

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        kind = (
            "class" if isinstance(node, ast.ClassDef)
            else "async_function" if isinstance(node, ast.AsyncFunctionDef)
            else "function"
        )

        sig_line = lines[node.lineno - 1].strip()
        end_line = getattr(node, "end_lineno", node.lineno)
        docstring = ast.get_docstring(node) or ""

        decorators = []
        for dec in getattr(node, "decorator_list", []):
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)

        parent_node = parent_map.get(id(node))
        parent = parent_node.name if isinstance(parent_node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else None

        calls_made: set[str] = set()
        body_tokens: set[str] = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls_made.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls_made.add(child.func.attr)

            if isinstance(child, ast.Name):
                body_tokens.add(child.id)
            elif isinstance(child, ast.Attribute):
                body_tokens.add(child.attr)

        code = "\n".join(lines[node.lineno - 1 : end_line])

        symbols[node.name] = {
            "name": node.name,
            "type": kind,
            "parent": parent,
            "start_line": node.lineno,
            "end_line": end_line,
            "signature": sig_line,
            "docstring": docstring,
            "decorators": decorators,
            "calls_made": calls_made,
            "body_tokens": body_tokens,
            "code": code,
        }

    return symbols

def _build_call_graph(symbols: dict[str, dict]) -> dict[str, dict]:
    """Resolve in-file callees and callers for every symbol."""
    known = set(symbols.keys())
    for name, sym in symbols.items():
        sym["callees"] = sym["calls_made"] & known
        sym["callers"] = set()

    for name, sym in symbols.items():
        for callee in sym["callees"]:
            symbols[callee]["callers"].add(name)

    return symbols

# ---------------------------------------------------------------------------
# 2. Weighted Scoring & Query Matching
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())

def _expand_identifier(name: str) -> list[str]:
    parts = name.replace("-", "_").split("_")
    expanded = []
    for part in parts:
        subs = re.sub(r"([A-Z])", r" \1", part).split()
        expanded.extend(s.lower() for s in subs if s)
    return expanded or [name.lower()]

def _score(query_tokens: list[str], sym: dict) -> float:
    weights = {
        "name": 5.0,
        "docstring": 3.0,
        "signature": 2.0,
        "callee_names": 2.5,
        "caller_names": 1.5,
        "body_tokens": 0.8,
        "decorators": 1.0,
    }

    fields: dict[str, list[str]] = {
        "name": _expand_identifier(sym["name"]),
        "docstring": _tokenize(sym["docstring"]),
        "signature": _tokenize(sym["signature"]),
        "callee_names": [t for c in sym.get("callees", set()) for t in _expand_identifier(c)],
        "caller_names": [t for c in sym.get("callers", set()) for t in _expand_identifier(c)],
        "body_tokens": list(sym["body_tokens"]),
        "decorators": [t for d in sym["decorators"] for t in _expand_identifier(d)],
    }

    score = 0.0
    for token in query_tokens:
        for field_name, tokens in fields.items():
            if not tokens:
                continue
            matches = tokens.count(token)
            if matches:
                score += weights[field_name] * (1 + math.log(matches))
            else:
                partials = sum(1 for t in tokens if token in t or t in token)
                if partials:
                    score += weights[field_name] * 0.35 * partials
    return score

def _score_symbols(question: str, symbols: dict[str, dict]) -> list[tuple[float, dict]]:
    raw_tokens = _tokenize(question)
    expanded = [w for t in raw_tokens for w in _expand_identifier(t)]
    query_tokens = list(set(raw_tokens + expanded))

    scored = []
    for sym in symbols.values():
        s = _score(query_tokens, sym)
        if s > 0:
            scored.append((s, sym))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored

# ---------------------------------------------------------------------------
# 3. Connection Resolver & Public API
# ---------------------------------------------------------------------------

@dataclass
class SymbolResult:
    symbol: dict
    score: float
    code: str
    file: str
    connections: list = field(default_factory=list)

    def __repr__(self) -> str:
        sym = self.symbol
        parent_str = f" (in {sym['parent']})" if sym["parent"] else ""
        header = (
            f"[{sym['type']}] {sym['name']}{parent_str} "
            f"L{sym['start_line']}–{sym['end_line']}  score={self.score:.2f}"
        )
        doc = f"\n  \"{sym['docstring'][:120]}\"" if sym["docstring"] else ""
        bar = "═" * min(len(header), 80)

        callees = sym.get("callees", set())
        callers = sym.get("callers", set())
        links = ""
        if callees:
            links += f"\n  calls   → {', '.join(sorted(callees))}"
        if callers:
            links += f"\n  called by <- {', '.join(sorted(callers))}"

        body = f"\n{bar}\n{self.code}\n"

        connected = ""
        if self.connections:
            connected = "\n── connected code ──────────────────────────────────────\n"
            for c in self.connections:
                csym = c.symbol
                clabel = f"  [{csym['type']}] {csym['name']} L{csym['start_line']}–{csym['end_line']}"
                connected += f"{clabel}\n{'─'*60}\n{c.code}\n\n"

        return f"{header}{doc}{links}{body}{connected}"

def _resolve_connections(
    sym: dict,
    symbols: dict[str, dict],
    depth: int,
    direction: str,
    _visited: set | None = None,
) -> list[SymbolResult]:
    if depth == 0:
        return []
    _visited = _visited or set()
    _visited.add(sym["name"])

    targets: set[str] = set()
    if direction in ("callees", "both"):
        targets |= sym.get("callees", set())
    if direction in ("callers", "both"):
        targets |= sym.get("callers", set())

    results = []
    for name in sorted(targets):
        if name in _visited or name not in symbols:
            continue
        connected_sym = symbols[name]
        sub = _resolve_connections(connected_sym, symbols, depth - 1, direction, _visited)
        results.append(SymbolResult(
            symbol={k: v for k, v in connected_sym.items() if k not in ("body_tokens", "calls_made")},
            score=0.0,
            code=connected_sym["code"],
            file="",
            connections=sub,
        ))
    return results

def query(
    file_path: str,
    question: str,
    top_k: int = 3,
    min_score: float = 0.0,
    depth: int = 2,
    direction: str = "both",
) -> list[SymbolResult]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    lines = source.splitlines()
    symbols = _extract_symbols(file_path, source, lines)
    symbols = _build_call_graph(symbols)
    scored = _score_symbols(question, symbols)

    results = []
    for score, sym in scored[:top_k]:
        if score < min_score:
            continue
        connections = _resolve_connections(sym, symbols, depth=depth, direction=direction)
        clean_sym = {k: v for k, v in sym.items() if k not in ("body_tokens", "calls_made")}
        results.append(SymbolResult(
            symbol=clean_sym,
            score=round(score, 4),
            code=sym["code"],
            file=file_path,
            connections=connections,
        ))
    return results