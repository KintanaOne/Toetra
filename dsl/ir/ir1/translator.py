from __future__ import annotations

from dsl.ast.nodes.program import ProgramNode
from dsl.ast.nodes.property import PropertyNode

from dsl.ir.ir1.nodes import VerificationTask
from dsl.ir.ir1.scope_translator import ScopeTranslator
from dsl.ir.ir1.query_translator import QueryTranslator

from dsl.language.vocabulary.backends import EnumBackend


class IRTranslator:
    """
    AST validated by semantic layer -> IR1 verification tasks.

    Responsibility:
        ProgramNode / PropertyNode -> VerificationTask

    Detailed translation is delegated to:
        - ScopeTranslator
        - QueryTranslator
    """

    def __init__(
        self,
        scope_translator: ScopeTranslator | None = None,
        query_translator: QueryTranslator | None = None,
    ):
        self.scope_translator = scope_translator or ScopeTranslator()
        self.query_translator = query_translator or QueryTranslator()

    # ------------------------------------------------------------------
    # PROGRAM
    # ------------------------------------------------------------------

    def translate(self, program: ProgramNode) -> list[VerificationTask]:
        return [
            self._translate_property(prop)
            for prop in program.body
        ]

    # ------------------------------------------------------------------
    # PROPERTY
    # ------------------------------------------------------------------

    def _translate_property(self, prop: PropertyNode) -> VerificationTask:
        scope_ir = self.scope_translator.translate(prop.rule.scope)
        query_ir = self.query_translator.translate(prop.rule.assertion.root)

        backend = self._translate_backend(prop)

        return VerificationTask(
            property_type=prop.type,
            scope=scope_ir,
            query=query_ir,
            backend=backend,
        )

    # ------------------------------------------------------------------
    # BACKEND
    # ------------------------------------------------------------------

    def _translate_backend(self, prop: PropertyNode) -> EnumBackend | None:
        if prop.backend is None:
            return None

        backend_name = prop.backend.name

        return EnumBackend[backend_name]