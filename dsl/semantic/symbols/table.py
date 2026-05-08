from dsl.semantic.symbols.symbol import Symbol


class SymbolTable:
    """
    Central semantic symbol registry.

    Responsibilities:
    - register semantic variables
    - resolve symbols by name
    - expose semantic lookup utilities

    Example:
        x  -> anchor
        x' -> perturbation
        _x -> symbolic quantifier variable
    """

    def __init__(self):
        self.symbols = {}

    # ─────────────────────────────────────────────
    # REGISTER
    # ─────────────────────────────────────────────

    def register(self, symbol: Symbol):
        """
        Register a semantic symbol.

        Raises:
            ValueError:
                if the symbol already exists.
        """

        if symbol.name in self.symbols:
            raise ValueError(
                f"Symbol '{symbol.name}' already registered"
            )

        self.symbols[symbol.name] = symbol

    # ─────────────────────────────────────────────
    # RESOLVE
    # ─────────────────────────────────────────────

    def resolve(self, name: str):
        """
        Resolve a symbol by name.

        Returns:
            Symbol | None
        """

        return self.symbols.get(name)

    # ─────────────────────────────────────────────
    # EXISTS
    # ─────────────────────────────────────────────

    def exists(self, name: str) -> bool:
        """
        Check whether a symbol exists.
        """

        return name in self.symbols

    # ─────────────────────────────────────────────
    # ITERATION
    # ─────────────────────────────────────────────

    def all(self):
        """
        Return all registered symbols.
        """

        return list(self.symbols.values())

    # ─────────────────────────────────────────────
    # DEBUG
    # ─────────────────────────────────────────────

    def __repr__(self):
        return (
            f"SymbolTable("
            f"symbols={list(self.symbols.keys())}"
            f")"
        )