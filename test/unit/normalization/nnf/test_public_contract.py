from __future__ import annotations

from test.fixtures.normalization.nnf.helpers import import_nnf_normalizer_cls, import_run_nnf



def test_nnf_normalizer_public_api_contract():
    cls = import_nnf_normalizer_cls()
    normalizer = cls()

    assert hasattr(normalizer, "normalize_expr")
    assert hasattr(normalizer, "normalize_query")
    assert hasattr(normalizer, "normalize_task")
    assert hasattr(normalizer, "normalize_tasks")



def test_run_nnf_public_entrypoint_contract():
    run_nnf = import_run_nnf()

    assert callable(run_nnf)
