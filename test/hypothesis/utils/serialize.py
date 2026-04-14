from hypothesis import strategies as st

def serialize(ast):
    if isinstance(ast, str):
        return f'"{ast}"'
    elif isinstance(ast, list):
        return "[" + ", ".join(serialize(x) for x in ast) + "]"
    elif isinstance(ast, dict):
        items = ", ".join(f"{serialize(k)}: {serialize(v)}" for k, v in ast.items())
        return "{" + items + "}"
    else:
        return str(ast)