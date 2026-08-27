from __future__ import annotations

from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid4, uuid5

import pytest

from core.app.material_receipts.actor_provenance import authorize_candidate_creation_actor
from core.app.material_receipts.results import ReviewApplicationError, ReviewFailureCode
from core.app.material_receipts.review_use_cases import ActorContext


def assert_code(value: object, code: ReviewFailureCode) -> None:
    with pytest.raises(ReviewApplicationError) as caught:
        authorize_candidate_creation_actor(value)
    assert caught.value.code is code


def test_exact_taxonomy_and_authorized_uuidv4() -> None:
    assert_code(None, ReviewFailureCode.ACTOR_REQUIRED)
    assert_code(object(), ReviewFailureCode.ACTOR_INVALID)
    assert_code(ActorContext("reviewer:review-7"), ReviewFailureCode.ACTOR_UNAUTHORIZED)
    assert_code(ActorContext("operator:legacy-7"), ReviewFailureCode.ACTOR_UNAUTHORIZED)
    actor = ActorContext(f"operator:{uuid4()}")
    assert authorize_candidate_creation_actor(actor) == actor.actor_reference


@pytest.mark.parametrize(
    "suffix",
    [
        str(uuid4()).upper(),
        str(uuid1()),
        str(uuid3(NAMESPACE_DNS, "aios")),
        str(uuid5(NAMESPACE_DNS, "aios")),
        str(UUID(int=0)),
        "not-a-uuid",
        uuid4().hex,
    ],
)
def test_generic_valid_operator_values_are_deterministically_unauthorized(suffix: str) -> None:
    assert_code(ActorContext(f"operator:{suffix}"), ReviewFailureCode.ACTOR_UNAUTHORIZED)


def test_forged_corrupted_subclassed_and_reconstructed_objects_are_invalid() -> None:
    forged = object.__new__(ActorContext)
    assert_code(forged, ReviewFailureCode.ACTOR_INVALID)

    corrupted = ActorContext(f"operator:{uuid4()}")
    object.__setattr__(corrupted, "actor_reference", "password=secret")
    assert_code(corrupted, ReviewFailureCode.ACTOR_INVALID)

    class Subclass(ActorContext):
        pass

    subclassed = object.__new__(Subclass)
    object.__setattr__(subclassed, "actor_reference", f"operator:{uuid4()}")
    assert_code(subclassed, ReviewFailureCode.ACTOR_INVALID)
    assert_code({"actor_reference": f"operator:{uuid4()}"}, ReviewFailureCode.ACTOR_INVALID)


@pytest.mark.parametrize(
    "value",
    ["", "operator:", "system:actor", "operator:bad\nvalue", "operator:../admin",
     "operator:postgresql://user:password@host/db", "operator:SELECT * FROM secret",
     "operator:\N{CYRILLIC SMALL LETTER A}", "operator:{uuid}", "operator: uuid", "operator:uuid "],
)
def test_generic_invalid_or_prohibited_shaped_states_are_invalid(value: str) -> None:
    forged = object.__new__(ActorContext)
    object.__setattr__(forged, "actor_reference", value)
    assert_code(forged, ReviewFailureCode.ACTOR_INVALID)
