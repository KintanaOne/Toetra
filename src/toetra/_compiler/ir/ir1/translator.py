from __future__ import annotations

from toetra._compiler.ast.nodes.program import ProgramNode
from toetra._compiler.ast.nodes.property import PropertyNode

from toetra._compiler.ir.ir1.nodes import (
    RestrictionIR,
    RestrictionProvenanceIR,
    VerificationTask,
)
from toetra._compiler.ir.ir1.points import PointIRRegistry, copy_source_span
from toetra._compiler.ir.ir1.query_translator import QueryTranslator
from toetra._compiler.ir.ir1.scalar_translator import ScalarExpressionTranslator
from toetra._compiler.ir.ir1.scope_translator import ScopeTranslator

from toetra._language.vocabulary.backends import EnumBackend


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
        self.point_registry = PointIRRegistry()

        if scope_translator is None and query_translator is None:
            scalar_translator = ScalarExpressionTranslator(self.point_registry)
            self.scope_translator = ScopeTranslator(
                scalar_translator=scalar_translator,
                point_registry=self.point_registry,
            )
            self.query_translator = QueryTranslator(
                scalar_translator=scalar_translator,
            )
        else:
            self.scope_translator = scope_translator or ScopeTranslator(
                point_registry=self.point_registry,
            )
            self.query_translator = query_translator or QueryTranslator()

    # ------------------------------------------------------------------
    # PROGRAM
    # ------------------------------------------------------------------

    def translate(self, program: ProgramNode) -> list[VerificationTask]:
        return [self._translate_property(prop) for prop in program.body]

    # ------------------------------------------------------------------
    # PROPERTY
    # ------------------------------------------------------------------

    def _translate_property(self, prop: PropertyNode) -> VerificationTask:
        self.point_registry.clear()

        semantic = prop.semantic
        context = semantic.context if semantic is not None else None

        if context is not None:
            for frame in context.binder_frames:
                self.point_registry.register_frame(frame)

        restriction_ir = None
        if (
            semantic is not None
            and semantic.restriction_root is not None
            and context is not None
            and context.restriction_provenance is not None
        ):
            restriction_ir = RestrictionIR(
                expression=self.query_translator.translate_expression(
                    semantic.restriction_root
                ),
                provenance=RestrictionProvenanceIR(
                    origin=context.restriction_provenance.origin.value,
                    source_span=copy_source_span(
                        context.restriction_provenance.source_span
                    ),
                ),
            )

        scope_ir = self.scope_translator.translate(
            prop.rule.scope,
            context=context,
            restriction=restriction_ir,
        )

        logical_root = (
            semantic.logical_root
            if semantic is not None and semantic.logical_root is not None
            else prop.rule.assertion.root
        )
        query_ir = self.query_translator.translate(logical_root)

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

        backend = prop.backend.name

        if isinstance(backend, EnumBackend):
            return backend

        return EnumBackend.from_str(str(backend))
