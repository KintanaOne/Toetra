from __future__ import annotations

from toetra._compiler.semantic.symbols.point import PointSymbol
from toetra._compiler.semantic.symbols.symbol import Symbol

SemanticSymbol = Symbol | PointSymbol


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

    def register(self, symbol: SemanticSymbol) -> None:
        """
        Register a semantic symbol.

        Raises:
            ValueError:
                if the symbol already exists.
        """

        if symbol.name in self.symbols:
            raise ValueError(f"Symbol '{symbol.name}' already registered")

        self.symbols[symbol.name] = symbol

    # ─────────────────────────────────────────────
    # RESOLVE
    # ─────────────────────────────────────────────

    def resolve(self, name: str) -> SemanticSymbol | None:
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

    def all(self) -> list[SemanticSymbol]:
        """
        Return all registered symbols.
        """

        return list(self.symbols.values())

    # ─────────────────────────────────────────────
    # DEBUG
    # ─────────────────────────────────────────────

    def __repr__(self):
        return f"SymbolTable(" f"symbols={list(self.symbols.keys())}" f")"
