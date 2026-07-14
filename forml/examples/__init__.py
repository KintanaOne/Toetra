"""Small packaged policies used by the documentation and executable examples."""

from importlib.resources import files


def credit_risk_policy() -> str:
    """Return the packaged affine credit-risk policy as FORML source text."""

    resource = files("forml.examples").joinpath("credit_risk_policy.forml")
    return resource.read_text(encoding="utf-8")


__all__ = ["credit_risk_policy"]
