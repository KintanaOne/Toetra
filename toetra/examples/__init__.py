"""Small packaged policies used by the documentation and executable examples."""

from importlib.resources import files


def credit_risk_policy() -> str:
    """Return the packaged affine credit-risk policy as specification source text."""

    resource = files("toetra.examples").joinpath("credit_risk_policy.toetra")
    return resource.read_text(encoding="utf-8")


__all__ = ["credit_risk_policy"]
