import json
from typing import Dict, List, Optional


# ----------------------------------------------------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------------------------------------------------

def quote_if_needed(value: str) -> str:
    if value is None:
        return ""

    # simple heuristic: quote if contains special chars
    if any(c in value for c in ['/', '.', '-', ' ']):
        return f'"{value}"'

    return value


def format_args(args: Dict[str, str]) -> str:
    if not args:
        return ""

    parts = []
    for k, v in args.items():
        if v is True:
            parts.append(k)
        else:
            parts.append(f"{k}={v}")

    return ", ".join(parts)


def flatten(d, prefix=""):
    parts = []
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            parts.extend(flatten(v, key))
        else:
            parts.append(f"{key}={v}")
    return parts


def flatten_no_prefix(d):
    parts = []
    for k, v in d.items():
        if isinstance(v, dict):
            parts.extend(flatten_no_prefix(v))
        else:
            parts.append(f"{k}={v}")
    return parts

# "variable=x0, metric=L2, radius=0.01, name=input_domain, values=['x0', 'x1']"


# ----------------------------------------------------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------------------------------------------------

def serialize_header(d: Dict) -> str:
    model = quote_if_needed(d.get("model"))
    target = d.get("target")

    lines = [
        f"model := {model}",
        f"target := {target}"
    ]

    return "\n".join(lines)


# ----------------------------------------------------------------------------------------------------------------------
# PROPERTY PARTS
# ----------------------------------------------------------------------------------------------------------------------

def serialize_quantifier(prop: Dict) -> str:
    expr = prop.get("expr")

    q = expr.get("quantifier")
    domain = serialize_domain(expr)

    return " ".join(filter(None, [q, domain]))

    
def serialize_at(prop: Dict) -> str:
    expr = prop.get("expr")
    at = expr.get("at")

    var = at.get("variable")
    neigh = serialize_neighborhood(at.get("neighborhood"))
    domain = serialize_domain(at)

    return " ".join(filter(None, [f"at {var}", neigh, domain]))
    

def serialize_check_at(prop: Dict) -> str:
    if not prop.get("check_at"):
        return "check_at " + prop.get("check_at")
    

def serialize_pairwise(prop: Dict) -> str:
    expr = prop.get("expr")

    pair = expr.get("pairwise", {}).get("pairwise")
    neigh = serialize_neighborhood(expr.get("pairwise", {}).get("neighborhood"))
    domain = serialize_domain(expr.get("pairwise"))

    return " ".join(filter(None, [pair, neigh, domain]))


def serialize_domain(d: Dict) -> str:
    domain = d.get("domain")
    if not domain:
        return ""

    name = domain["name"]
    values = ", ".join(f'"{v}"' for v in domain["values"])

    return f"with {name}({values})"


def serialize_neighborhood(neigh: Dict) -> str:
    if not neigh:
        return ""

    metric = neigh.get("metric")
    args = neigh.get("args", {})

    parts = []

    if metric:
        parts.append(f"metric={metric}")

    if args:
        parts.append(format_args(args))

    inner = ", ".join(parts)

    return f"in neighborhood({inner})"


def serialize_property_expr(prop: Dict) -> str:
    mode = prop.get("expr").get("mode")

    # ---- QUANTIFIER ----
    if mode == "quantifier":
        quantifier = serialize_quantifier(prop)

        return quantifier

    # ---- PAIRWISE ----
    if mode == "pairwise":
        pairwise = serialize_pairwise(prop)
        return pairwise

    # ---- FUTURE EXTENSIONS ----
    if mode == "at":
        at = serialize_at(prop)
        return at

    if mode == "check_at":
        return "check_at x"

    return "forall"


def serialize_assertion(assertion: Dict) -> str:
    if not assertion:
        return ""

    t = assertion.get("type")

    if t == "implication":
        return f"{serialize_assertion(assertion['left'])} -> {serialize_assertion(assertion['right'])}"

    if t == "or":
        return " OR ".join(serialize_assertion(o) for o in assertion["operands"])

    if t == "and":
        return " AND ".join(serialize_assertion(o) for o in assertion["operands"])

    if t == "not":
        return f"NOT {serialize_assertion(assertion['operand'])}"

    if t == "comparison":
        return f"{assertion['left']} {assertion['op']} {assertion['right']}"

    if t == "problem":
        return assertion["value"]

    return "UNKNOWN"


def serialize_abstractor(prop: Dict) -> str:
    abs_ = prop.get("abstractor")
    if not abs_:
        return ""

    name = abs_["name"]
    args = format_args(abs_["args"])

    if args:
        return f"using {name}({args})"

    return f"using {name}"


# ----------------------------------------------------------------------------------------------------------------------
# PROPERTY
# ----------------------------------------------------------------------------------------------------------------------

def serialize_property(prop: Dict) -> str:
    ptype = prop.get("type", "LOGIC")

    expr = serialize_property_expr(prop)
    assertion = serialize_assertion(prop.get("assertion"))

    base = f"[{ptype}]:\n {expr} => {assertion}"

    abstractor = serialize_abstractor(prop)

    return " ".join(filter(None, [base, abstractor]))


# ----------------------------------------------------------------------------------------------------------------------
# BODY
# ----------------------------------------------------------------------------------------------------------------------

def serialize_body(d: Dict) -> str:
    props = d.get("properties", [])

    return "\n\n".join(serialize_property(p) for p in props)


# ----------------------------------------------------------------------------------------------------------------------
# PROGRAM
# ----------------------------------------------------------------------------------------------------------------------

def dict_to_forml(d: Dict) -> str:
    header = serialize_header(d)
    body = serialize_body(d)

    return f"{header}\n\n{body}"

if __name__ == "__main__":
    # Example usage
    example_dict = {
    "model": "path/to/model.onnx",
    "target": "MyTargetColumn",
    "properties": [
        {
            "type": "ROBUSTNESS",
            "expr": {
                "mode": "at",
                "at": {
                    "variable": "x0",
                    "neighborhood": {
                        "metric": "L2",
                        "args": {
                            "eps": "0.01"
                        }
                    },
                    "domain": {
                        "name": "sex",
                        "values": [
                            "male",
                            "female"
                        ]
                    }
                }
            },
            "abstractor": None
        }
    ]
}
    forml_code = dict_to_forml(example_dict)
    print(forml_code)