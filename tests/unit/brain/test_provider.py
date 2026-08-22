from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
import inspect
from pathlib import Path
from typing import get_type_hints

import pytest

from core.brain.inference_contracts import (
    InferenceCapability,
    InferenceRequest,
    InferenceResult,
)
from core.brain.provider import (
    InferenceProvider,
    ProviderDescriptor,
    ProviderRuntimeKind,
)


ROOT = Path(__file__).resolve().parents[3]
PROVIDER_PATH = ROOT / "core" / "brain" / "provider.py"


def make_descriptor(**overrides: object) -> ProviderDescriptor:
    values: dict[str, object] = {
        "provider_id": "provider",
        "model_id": "model",
        "runtime_kind": ProviderRuntimeKind.LOCAL,
        "capabilities": [InferenceCapability.STRUCTURED_INFERENCE],
    }
    values.update(overrides)
    return ProviderDescriptor(**values)  # type: ignore[arg-type]


class ConcreteProvider(InferenceProvider):
    def __init__(self, descriptor: ProviderDescriptor) -> None:
        self._descriptor = descriptor

    @property
    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        raise NotImplementedError


def test_runtime_kind_has_exact_values_and_no_aliases() -> None:
    assert [(item.name, item.value) for item in ProviderRuntimeKind] == [
        ("LOCAL", "local"),
        ("REMOTE", "remote"),
    ]
    assert len(ProviderRuntimeKind.__members__) == 2


def test_descriptor_is_frozen() -> None:
    descriptor = make_descriptor()
    with pytest.raises(FrozenInstanceError):
        descriptor.provider_id = "changed"  # type: ignore[misc]


def test_descriptor_uses_slots() -> None:
    assert not hasattr(make_descriptor(), "__dict__")


def test_valid_provider_and_model_identifiers_are_preserved() -> None:
    descriptor = make_descriptor(provider_id="opaque:id", model_id="opaque/model")
    assert descriptor.provider_id == "opaque:id"
    assert descriptor.model_id == "opaque/model"


@pytest.mark.parametrize("field_name", ["provider_id", "model_id"])
@pytest.mark.parametrize("value", ["", " ", "x" * 129, "x\n", "x\x7f"])
def test_invalid_identifiers_are_rejected(field_name: str, value: str) -> None:
    with pytest.raises(ValueError):
        make_descriptor(**{field_name: value})


@pytest.mark.parametrize("field_name", ["provider_id", "model_id"])
@pytest.mark.parametrize("value", [None, 1, b"identifier"])
def test_non_string_identifiers_are_rejected(
    field_name: str, value: object
) -> None:
    with pytest.raises(TypeError):
        make_descriptor(**{field_name: value})


@pytest.mark.parametrize("field_name", ["provider_id", "model_id"])
def test_identifier_maximum_is_128_characters(field_name: str) -> None:
    descriptor = make_descriptor(**{field_name: "x" * 128})
    assert getattr(descriptor, field_name) == "x" * 128


@pytest.mark.parametrize(
    "runtime_kind", [ProviderRuntimeKind.LOCAL, ProviderRuntimeKind.REMOTE]
)
def test_local_and_remote_descriptors_are_valid(
    runtime_kind: ProviderRuntimeKind,
) -> None:
    assert make_descriptor(runtime_kind=runtime_kind).runtime_kind is runtime_kind


@pytest.mark.parametrize("runtime_kind", ["local", "remote", None, object()])
def test_invalid_runtime_kind_is_rejected(runtime_kind: object) -> None:
    with pytest.raises(TypeError):
        make_descriptor(runtime_kind=runtime_kind)


def test_capabilities_are_defensively_snapshotted_as_tuple() -> None:
    source = [InferenceCapability.STRUCTURED_INFERENCE]
    descriptor = make_descriptor(capabilities=source)
    source.clear()
    assert descriptor.capabilities == (
        InferenceCapability.STRUCTURED_INFERENCE,
    )
    assert isinstance(descriptor.capabilities, tuple)


@pytest.mark.parametrize(
    "capabilities",
    [
        [],
        [
            InferenceCapability.STRUCTURED_INFERENCE,
            InferenceCapability.STRUCTURED_INFERENCE,
        ],
        ["structured_inference"],
        [object()],
        "structured_inference",
        None,
    ],
)
def test_non_exact_capability_sets_are_rejected(capabilities: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_descriptor(capabilities=capabilities)


def test_descriptor_has_exactly_four_fields() -> None:
    assert [field.name for field in fields(ProviderDescriptor)] == [
        "provider_id",
        "model_id",
        "runtime_kind",
        "capabilities",
    ]


def test_descriptor_has_no_prohibited_fields() -> None:
    names = {field.name.lower() for field in fields(ProviderDescriptor)}
    prohibited = {
        "endpoint",
        "base_url",
        "credential",
        "credentials",
        "api_key",
        "account",
        "account_id",
        "tenant",
        "timeout",
        "retry",
        "persistence",
        "session",
        "cache",
        "history",
        "concurrency",
        "cpu",
        "ram",
        "model_size",
        "pricing",
        "tools",
        "business",
    }
    assert names.isdisjoint(prohibited)


def test_inference_provider_and_members_are_abstract() -> None:
    assert inspect.isabstract(InferenceProvider)
    assert InferenceProvider.descriptor.__isabstractmethod__
    assert InferenceProvider.infer.__isabstractmethod__
    with pytest.raises(TypeError):
        InferenceProvider()


def test_descriptor_property_is_read_only() -> None:
    provider = ConcreteProvider(make_descriptor())
    assert provider.descriptor == make_descriptor()
    with pytest.raises(AttributeError):
        provider.descriptor = make_descriptor(model_id="other")  # type: ignore[misc]


def test_infer_is_async_with_exact_signature_and_annotations() -> None:
    assert inspect.iscoroutinefunction(InferenceProvider.infer)
    signature = inspect.signature(InferenceProvider.infer)
    assert list(signature.parameters) == ["self", "request"]
    assert signature.parameters["request"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    hints = get_type_hints(InferenceProvider.infer)
    assert hints == {"request": InferenceRequest, "return": InferenceResult}


def test_descriptor_property_has_exact_return_annotation() -> None:
    assert get_type_hints(InferenceProvider.descriptor.fget) == {
        "return": ProviderDescriptor
    }


def test_provider_module_imports_are_approved_only() -> None:
    tree = ast.parse(PROVIDER_PATH.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    assert imports == {
        "__future__",
        "abc",
        "dataclasses",
        "enum",
        "core.brain.inference_contracts",
    }


def test_provider_module_contains_no_execution_or_prohibited_ownership() -> None:
    source = PROVIDER_PATH.read_text(encoding="utf-8").lower()
    prohibited = (
        "httpx",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "create_subprocess",
        "core.aios_core",
        "core.registry",
        "core.event",
        "telegram",
        "memory",
        "specialist",
        "business",
        "database",
    )
    assert not any(marker in source for marker in prohibited)


def test_provider_module_has_no_provider_sdk_or_brand_imports() -> None:
    source = PROVIDER_PATH.read_text(encoding="utf-8").lower()
    prohibited_brands = ("ollama", "openai", "anthropic", "gemini")
    assert not any(brand in source for brand in prohibited_brands)


def test_core_has_no_reverse_provider_dependency() -> None:
    offenders: list[str] = []
    for path in (ROOT / "core").rglob("*.py"):
        if path.parent == PROVIDER_PATH.parent:
            continue
        source = path.read_text(encoding="utf-8")
        if "core.brain.provider" in source or "from .brain" in source:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
