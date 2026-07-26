from __future__ import annotations

from dataclasses import dataclass, field

from toetra._compatibility.descriptors import BackendProfileDescriptor
from toetra._compatibility.enums import (
    CompatibilityClassification,
    ConclusionScope,
    SupportStatus,
)
from toetra._compatibility.errors import (
    AmbiguousCompatibilityRuleError,
    DuplicateCompatibilityRuleError,
)
from toetra._compatibility.model import (
    CompatibilityRule,
    NumericCompatibilityAssessment,
    NumericCompatibilityQuery,
)


@dataclass
class NumericCompatibilityRegistry:
    """Deterministic registry for framework/src/toetra/_models/encoder/backend rules."""

    _rules: list[CompatibilityRule] = field(default_factory=list)

    def register(self, rule: CompatibilityRule) -> None:
        if any(existing.pattern == rule.pattern for existing in self._rules):
            raise DuplicateCompatibilityRuleError(
                "A numeric compatibility rule is already registered for the "
                f"same normalized pattern: {rule.pattern!r}."
            )
        self._rules.append(rule)

    def assess(
        self,
        query: NumericCompatibilityQuery,
        *,
        backend_profile: BackendProfileDescriptor,
    ) -> NumericCompatibilityAssessment:
        if (
            query.contains_non_finite_values
            and not backend_profile.supports_non_finite_values
        ):
            return NumericCompatibilityAssessment(
                query=query,
                support_status=SupportStatus.UNSUPPORTED,
                classification=CompatibilityClassification.INCOMPATIBLE,
                semantic_target=backend_profile.profile_id,
                permitted_conclusions=frozenset(),
                conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
                diagnostics=(
                    "The verification task contains NaN or infinity, but the "
                    f"backend profile {backend_profile.profile_id!r} rejects "
                    "non-finite values.",
                ),
            )

        matches = [rule for rule in self._rules if rule.pattern.matches(query)]
        if not matches:
            return NumericCompatibilityAssessment(
                query=query,
                support_status=SupportStatus.UNSUPPORTED,
                classification=CompatibilityClassification.UNKNOWN,
                semantic_target="unknown",
                permitted_conclusions=frozenset(),
                conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
                diagnostics=(
                    "No framework/src/toetra/_models/encoder/backend numeric compatibility "
                    "rule matches this verification task.",
                ),
            )

        max_specificity = max(rule.pattern.specificity for rule in matches)
        winners = [
            rule for rule in matches if rule.pattern.specificity == max_specificity
        ]
        if len(winners) != 1:
            rule_ids = ", ".join(sorted(rule.rule_id for rule in winners))
            raise AmbiguousCompatibilityRuleError(
                "Equally specific numeric compatibility rules match the task: "
                f"{rule_ids}."
            )

        rule = winners[0]
        return NumericCompatibilityAssessment(
            query=query,
            support_status=rule.support_status,
            classification=rule.classification,
            semantic_target=rule.semantic_target,
            permitted_conclusions=rule.permitted_conclusions,
            conclusion_scope=rule.conclusion_scope,
            matched_rule_id=rule.rule_id,
            evidence_id=rule.evidence_id,
            assumptions_and_preconditions=rule.assumptions_and_preconditions,
            replay_required_for=rule.replay_required_for,
            diagnostics=rule.diagnostics,
            documentation_reference=rule.documentation_reference,
        )

    def all(self) -> tuple[CompatibilityRule, ...]:
        return tuple(self._rules)

    def clear(self) -> None:
        self._rules.clear()
