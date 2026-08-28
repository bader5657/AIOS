from __future__ import annotations

import importlib
import sys
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid4, uuid5

import pytest

from core.app.material_receipts.results import ReviewApplicationError, ReviewFailureCode


def policy():
    from core.app.material_receipts.actor_provenance import (
        authorize_candidate_creation_actor_reference,
    )
    return authorize_candidate_creation_actor_reference


def assert_unauthorized(value: str) -> None:
    with pytest.raises(ReviewApplicationError) as caught:
        policy()(value)
    assert caught.value.code is ReviewFailureCode.ACTOR_UNAUTHORIZED
    assert caught.value.__cause__ is None


def test_authorizes_only_exact_canonical_lowercase_rfc4122_uuidv4() -> None:
    reference = f"operator:{uuid4()}"
    assert policy()(reference) == reference
    for suffix in (
        str(uuid4()).upper(),
        str(uuid1()),
        str(uuid3(NAMESPACE_DNS, "aios")),
        str(uuid5(NAMESPACE_DNS, "aios")),
        str(UUID(int=0)),
        "550e8400-e29b-41d4-7716-446655440000",
        "not-a-uuid",
        uuid4().hex,
        "{" + str(uuid4()) + "}",
    ):
        assert_unauthorized(f"operator:{suffix}")
    for reference in ("reviewer:review-7", "operator:legacy-7", "system:actor", ""):
        assert_unauthorized(reference)


def test_import_order_reload_and_absent_mutable_authority_registry() -> None:
    actor_name = "core.app.material_receipts.actor_provenance"
    review_name = "core.app.material_receipts.review_use_cases"
    actor_module = importlib.import_module(actor_name)
    review_module = importlib.import_module(review_name)
    original_type = review_module.ActorContext

    assert not hasattr(actor_module, "_ACTOR_CONTEXT_TYPE")
    assert not hasattr(actor_module, "_register_actor_context_type")
    assert importlib.reload(actor_module) is actor_module
    assert policy()(f"operator:{uuid4()}").startswith("operator:")

    sys.modules.pop(actor_name, None)
    imported_actor_first = importlib.import_module(actor_name)
    assert not hasattr(imported_actor_first, "_ACTOR_CONTEXT_TYPE")
    assert importlib.import_module(review_name).ActorContext is original_type
    assert importlib.reload(imported_actor_first) is imported_actor_first
