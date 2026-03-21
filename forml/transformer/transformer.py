# forml/parser/forml_transformer.py

from pathlib import Path

from lark import Token, Transformer, Lark, Tree
from forml.parser.errors import (
    ParserAssertionError, ParserDomainError, ParserError, ParserHeaderError, ParserBodyError, ParserImplicationError, ParserLogicAssertionError, ParserLogicExprError, ParserProblemError,
    ParserSectionError, ParserDeclarationError, ParserPropertyError,
    ParserAnchorError, ParserAbstractorError, ParserBackendError, ParserFunctionError,
    ParserUniversalError
)
from forml.transformer.helper import print_tree
from forml.transformer.nodes import *


class FORMLTransformer(Transformer):
    """Transforms Lark parse tree into Python Node objects, with validation."""

    # ────────────────────────────── Utilities ──────────────────────────────

    # Recursive search for a node of a specific type in the tree
    def find_node(self, node, node_type):

        # if it's a list, we need to check each item
        if isinstance(node, list):
            for item in node:
                result = self.find_node(item, node_type)
                if result:
                    return result

        # if it's a Tree, we need to check its children
        elif isinstance(node, Tree):
            for child in node.children:
                result = self.find_node(child, node_type)
                if result:
                    return result

        # if it's the node type we're looking for, return it
        elif isinstance(node, node_type):
            return node

        return None
    
    def find_nodes(self, node, node_type):
        found = []

        if isinstance(node, node_type):
            found.append(node)

        if isinstance(node, Tree):
            for child in node.children:
                found.extend(self.find_nodes(child, node_type))

        return found


    def extract_value(self, node):
        """Safely extract the string value from a Token or Tree."""
        if isinstance(node, Token):
            return node.value
        elif isinstance(node, Tree):
            if not node.children:
                return node.data
            return self.extract_value(node.children[0])
        return str(node)

    # ────────────────────────────── Program ──────────────────────────────

    def program(self, items):
        if not items:
            raise ParserError("Program is empty or malformed.")
        header = next((i for i in items if isinstance(i, Header)), None)
        body = next((i for i in items if isinstance(i, Body)), None)
        footer = next((i for i in items if isinstance(i, Footer)), None)
        if not header:
            raise ParserHeaderError("Header is missing in the program.")
        if not body:
            raise ParserBodyError("Body is missing in the program.")
        return Program(header=header, body=body, footer=footer)

    # ────────────────────────────── Header / Footer ───────────────────────

    def comment(self, items):
        value = "".join(items).strip()
        if not value:
            raise ParserHeaderError("Empty comment detected.")
        return Comment(value=value)

    def inline_comment(self, items):
        value = "".join(items).strip()
        return Comment(value=value)

    def model_declaration(self, items):
        path_token = self.extract_value(items[0])
        return ModelDeclaration(path=path_token.strip('"'))
    
    def target_declaration(self, items):
        target = self.extract_value(items[0])
        return TargetDeclaration(target=target)

    def header(self, items):
        comments = [i for i in items if isinstance(i, Comment)]
        target = next((i for i in items if isinstance(i, TargetDeclaration)), None)
        model = next((i for i in items if isinstance(i, ModelDeclaration)), None)
        return Header(comments=comments, target=target, model=model)

    def footer(self, items):
        comments = [i for i in items if isinstance(i, Comment)]
        return Footer(comments=comments)

    # ────────────────────────────── Body ────────────────────────────────

    def body(self, items):
        sections = [i for i in items if isinstance(i, Section)]
        if not sections:
            raise ParserBodyError("Body has no sections.")
        return Body(sections=sections)
    
    def section(self, items):
        section = next((i for i in items if isinstance(i, (DeclarationSection, PropertySection))), None)
        if not section:
            raise ParserSectionError("Section is invalid or missing.")
        return section
    
    def declaration_section(self, items):
        if len(items) != 2:
            raise ParserDeclarationError("Declaration must have key and value.")
        return DeclarationSection(key=items[0], value=items[1])

    # ────────────────────────────── Universal & Anchor ─────────────────────

    def universal_expr(self, items):
        if len(items) != 2:
            raise ParserUniversalError("Universal expression requires quantifier and variable.")
        quantifier = self.extract_value(items[0])
        variable = self.extract_value(items[1])
        return UniversalExpr(quantifier=quantifier, variable=variable)

    def domain(self, items):
        """
        domain : "with" identifier "(" value ("," value)* ")"
        """
        if len(items) < 2:
            raise ParserDomainError("Invalid domain expression.")
        
        name = self.extract_value(items[0])  # ← identifiant après 'with'
        values = [self.extract_value(v) for v in items[1:]]
        return Domain(name=name, values=values)


    def anchor_expr(self, items):
        """
        anchor_expr : "at" identifier ("in" universal_expr)? (domain)?
        """
        if not items:
            raise ParserAnchorError("Empty anchor expression.")

        # get anchor (must be first)
        anchor = self.extract_value(items[0])

        # optional
        set_expr = None
        domain = None

        # try to find universal_expr and domain in items
        set_expr = self.find_node(items, UniversalExpr)
        domain = self.find_node(items, Domain)

        return AnchorExpr(anchor=anchor, set_expr=set_expr, domain=domain)

    def check_expr(self, items):
        if not items:
            raise ParserError("Empty check expression.")
        return CheckExpr(check=self.extract_value(items[0]))


    def symbolic_distance(self, items):
        """
        symbolic_distance : "distance" "(" identifier "," identifier "," value ")"
        """
        if len(items) != 3:
            raise ParserPropertyError(f"Invalid symbolic distance structure: {items}")

        feature = self.extract_value(items[0])
        distance_func_name = self.extract_value(items[1])
        threshold_value = self.extract_value(items[2])

        # Conversion de la fonction en EnumDistance
        try:
            distance_func_enum = EnumDistance[distance_func_name.upper()]
        except KeyError:
            raise ParserPropertyError(f"Unknown distance function '{distance_func_name}'.")

        # Conversion du seuil
        try:
            threshold = float(threshold_value)
        except ValueError:
            raise ParserPropertyError(f"Invalid threshold value: {threshold_value}")

        return {
            "feature": feature,
            "distance_func": distance_func_enum,
            "threshold": threshold,
        }

    def pairwise_expr(self, items):
        """
        pairwise_expr : identifier "~" identifier "with" symbolic_distance
        """
        if len(items) != 3:
            raise ParserPropertyError(f"Invalid pairwise expression: {items}")

        left = self.extract_value(items[0])
        right = self.extract_value(items[1])
        symbolic = items[2]

        if not isinstance(symbolic, dict):
            raise ParserPropertyError("Symbolic distance did not produce a valid dict.")

        return PairwiseExpr(
            left=left,
            right=right,
            feature=symbolic["feature"],
            distance_func=symbolic["distance_func"],
            threshold=symbolic["threshold"],
        )



    # ────────────────────────────── Property ─────────────────────────────

    def property(self, items):
        if len(items) < 2:
            raise ParserPropertyError("Property incomplete (type or assertion missing).")

        property_type = self.extract_value(items[0])
        universal_expr = self.find_node(items, UniversalExpr)   # we are looking for a UniversalExpr
        anchor_expr = self.find_node(items, AnchorExpr)         # we are looking for an AnchorExpr
        check_expr = self.find_node(items, CheckExpr)           # we are looking for a CheckExpr
        pairwise_expr = self.find_node(items, PairwiseExpr)     # we are looking for a PairwiseExpr
        assertion = self.find_node(items, Assertion)            # we are looking for an Assertion

        return Property(
            property_type=property_type,
            universal_expr=universal_expr,
            anchor_expr=anchor_expr,
            check_expr=check_expr,
            pairwise_expr=pairwise_expr,
            assertion=assertion
        )

    def property_section(self, items):
        if len(items) < 1:
            raise ParserPropertyError("Property section is empty.")
        
        # We need to find the Property node and the Abstractor node (if it exists) among the items
        prop = self.find_node(items, Property)
        abstractor = self.find_node(items, Abstractor)

        return PropertySection(property=prop, abstractor=abstractor)

    # ────────────────────────────── Assertions ─────────────────────

    def logic_expr(self, items):
        """
        [NOT] identifier comparison value
        """
        negate = False
        if len(items) == 4 and str(items[0]).upper() == "NOT":
            negate = True
            items = items[1:]

        if len(items) != 3:
            raise ParserLogicExprError(f"Invalid logic expression: {items}")

        key = self.extract_value(items[0])
        comparison = self.extract_value(items[1])
        value = self.extract_value(items[2])

        return LogicExpr(key=key, comparison=comparison, value=value, negate=negate)
    
    def logic_implication(self, items):
        if len(items) != 2:
            raise ParserImplicationError("Logic implication must have condition and consequence.")
        return LogicImplication(condition=items[0], consequence=items[1])
    
    def logic_assertion(self, items):
        if not items:
            raise ParserLogicAssertionError("Logic assertion is empty.")
        
        implications = self.find_nodes(items, LogicImplication)
        connections = [self.extract_value(i) for i in items if isinstance(i, Token) and str(i).upper() in {"AND", "OR"}]
        
        if len(implications) > 1 and not connections:
            raise ParserLogicAssertionError("Multiple implications without logical connections.")
        return LogicAssertion(implications=implications, connections=connections or None)

    # ────────────────────────────── Problem & Functions ─────────────────────

    def problem_expr(self, items):
        if len(items) != 2:
            raise ParserProblemError("Problem expression must have problem and function.")
        problem = self.extract_value(items[0])

        func_tree = items[1]
        function = self.find_node(func_tree, FunctionExpr)
        if function is None:
            raise ParserFunctionError(f"Invalid function in problem_expr: {func_tree}")
        return ProblemExpr(problem=problem, function=function)

    def function_expr(self, items):
        if not items:
            raise ParserFunctionError("Function is empty or invalid.")
        func_name = self.extract_value(items[0])

        # Extract arguments
        args = []
        if len(items) > 1:
            # items[1] can be an arg list or a Tree
            raw_args = items[1]
            if isinstance(raw_args, Tree) and raw_args.data == "args":
                args = [self.extract_value(arg) for arg in raw_args.children]
            else:
                args = [self.extract_value(raw_args)]
        try:
            func_enum = EnumFunction[func_name.upper()]
        except KeyError:
            raise ParserFunctionError(f"Unknown function '{func_name}'")
        return FunctionExpr(function=func_enum, args=args)

    # ────────────────────────────── Assertion Wrapper ─────────────────────

    def assertion(self, items):
        if not items:
            raise ParserAssertionError("Empty assertion.")
        expr = items[0]
        if isinstance(expr, (LogicAssertion, ProblemExpr)):
            return Assertion(expr=expr)
        raise ParserAssertionError(f"Invalid assertion type: {type(expr)}")

    # ────────────────────────────── Abstractors ─────────────────────────

    def backend(self, items):
        if len(items) != 1:
            raise ParserBackendError("Invalid backend definition.")
        name = self.extract_value(items[0])
        try:
            backend_enum = EnumBackend[name.upper()]
        except KeyError:
            raise ParserBackendError(f"Unknown backend '{name}'")
        return backend_enum

    def abstractor(self, items):
        if not items:
            raise ParserAbstractorError("Abstractor must have a backend.")
        backend = items[0]
        params = dict(items[1:]) if len(items) > 1 else {}
        return Abstractor(backend=backend, params=params)

    # ────────────────────────────── Terminals ───────────────────────────

    def identifier(self, items): return str(items[0])
    def string(self, items): return str(items[0]).strip('"')
    def number(self, items): return float(items[0]) if '.' in str(items[0]) else int(items[0])
    def boolean(self, items): return str(items[0]).lower() == "true"
    def comparison_op(self, items): return str(items[0])


# ────────────────────────────── Entry Point ──────────────────────────────

def transform_forml_code(code: str, grammar_path: str = "forml/grammar/forml_grammar.lark"):
    try:
        with open(grammar_path, "r", encoding="utf-8") as f:
            grammar = f.read()
        parser = Lark(grammar, start="program", parser="lalr")
        tree = parser.parse(code)
        print(tree.pretty())
        transformer = FORMLTransformer()
        return transformer.transform(tree)
    except Exception as e:
        raise ParserError(f"Transformation error: {e}")

def list_node_classes(self, node):
    classes = set()
    def recurse(n):
        classes.add(type(n).__name__)
        for c in getattr(n, '__dict__', {}).values():
            if isinstance(c, Node):
                recurse(c)
            elif isinstance(c, list):
                for x in c:
                    if isinstance(x, Node):
                        recurse(x)
    recurse(node)
    return classes


def print_node_tree(base_cls=Node, indent=0):
    """Affiche toutes les classes héritant de Node sous forme d'arbre."""
    prefix = " " * (indent * 2)
    print(f"{prefix}{base_cls.__name__}")
    for cls in base_cls.__subclasses__():
        print_node_tree(cls, indent + 1)


if __name__ == "__main__":
    test_path = Path(__file__).parent.parent / "example/00_simple_correct_example_multi_comment.forml"
    print(test_path)
    if test_path.exists():
        with open(test_path, "r", encoding="utf-8") as f:
            code = f.read()
    program = transform_forml_code(code)
    print_tree(program)