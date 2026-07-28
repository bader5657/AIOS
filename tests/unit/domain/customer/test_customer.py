import ast
import inspect
import unittest
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from core.domain.aggregate_root import AggregateRoot
from core.domain.customer import (
    Customer,
    CustomerAddress,
    CustomerCity,
    CustomerId,
    CustomerName,
)
from core.domain.customer.event_factory import CustomerEventFactory
from core.domain.customer.events import (
    CustomerAddressChanged,
    CustomerCityChanged,
    CustomerCreated,
    CustomerNameChanged,
    CustomerNotesChanged,
)
from core.domain.exceptions import DomainValidationError


class CustomerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.identity = CustomerId("customer-001")
        self.name = CustomerName("Customer One")
        self.address = CustomerAddress("First Address")
        self.city = CustomerCity("Mojokerto")
        self.source_calls: list[str] = []
        self.next_id = 0
        self.base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)

    def event_id_source(self) -> object:
        self.source_calls.append("id")
        self.next_id += 1
        return f"event-{self.next_id}"

    def occurred_at_source(self) -> datetime:
        self.source_calls.append("occurred_at")
        return self.base_time + timedelta(minutes=self.next_id)

    def make(
        self,
        notes: str | None = None,
        *,
        event_id_source: Callable[[], object] | None = None,
        occurred_at_source: Callable[[], datetime] | None = None,
    ) -> Customer:
        return Customer(
            self.identity,
            self.name,
            self.address,
            self.city,
            notes,
            event_id_source=event_id_source or self.event_id_source,
            occurred_at_source=occurred_at_source or self.occurred_at_source,
        )

    def test_constructor_signature_sources_and_exact_initial_state(self) -> None:
        signature = inspect.signature(Customer)
        self.assertEqual(
            tuple(signature.parameters),
            (
                "customer_id",
                "name",
                "address",
                "city",
                "notes",
                "event_id_source",
                "occurred_at_source",
            ),
        )
        self.assertEqual(signature.parameters["notes"].default, None)
        for name in ("event_id_source", "occurred_at_source"):
            self.assertEqual(
                signature.parameters[name].kind,
                inspect.Parameter.KEYWORD_ONLY,
            )
            self.assertIs(signature.parameters[name].default, inspect.Parameter.empty)
        with self.assertRaises(TypeError):
            Customer(self.identity, self.name, self.address, self.city)
        customer = self.make("  notes  ")
        self.assertIsInstance(customer, AggregateRoot)
        self.assertIs(customer.id, self.identity)
        self.assertEqual(
            (customer.name, customer.address, customer.city, customer.notes),
            (self.name, self.address, self.city, "  notes  "),
        )

    def test_constructor_records_exact_customer_created_once(self) -> None:
        notes = "  notes  "
        customer = self.make(notes)
        events = customer.pending_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertIs(type(event), CustomerCreated)
        self.assertEqual(event.id, "event-1")
        self.assertEqual(event.occurred_at, self.base_time + timedelta(minutes=1))
        self.assertEqual(event.event_name, "customer.created")
        self.assertIs(event.customer_id, self.identity)
        self.assertIs(event.name, self.name)
        self.assertIs(event.address, self.address)
        self.assertIs(event.city, self.city)
        self.assertIs(event.notes, notes)
        self.assertEqual(self.source_calls, ["id", "occurred_at"])

    def test_optional_notes_and_invalid_constructor_values(self) -> None:
        self.assertIsNone(self.make().notes)
        self.assertEqual(self.make("").notes, "")
        cases = (
            (None, self.name, self.address, self.city, None),
            ("id", self.name, self.address, self.city, None),
            (self.identity, None, self.address, self.city, None),
            (self.identity, "name", self.address, self.city, None),
            (self.identity, self.name, None, self.city, None),
            (self.identity, self.name, "address", self.city, None),
            (self.identity, self.name, self.address, None, None),
            (self.identity, self.name, self.address, "city", None),
            (self.identity, self.name, self.address, self.city, 1),
        )
        for values in cases:
            before = list(self.source_calls)
            with self.subTest(values=values), self.assertRaises(DomainValidationError):
                Customer(
                    *values,
                    event_id_source=self.event_id_source,
                    occurred_at_source=self.occurred_at_source,
                )
            self.assertEqual(self.source_calls, before)

    def test_non_callable_sources_are_rejected_without_invocation(self) -> None:
        cases = (
            (None, self.occurred_at_source),
            (self.event_id_source, None),
            (object(), self.occurred_at_source),
            (self.event_id_source, object()),
        )
        for event_id_source, occurred_at_source in cases:
            with self.subTest(
                event_id_source=event_id_source,
                occurred_at_source=occurred_at_source,
            ), self.assertRaises(DomainValidationError):
                Customer(
                    self.identity,
                    self.name,
                    self.address,
                    self.city,
                    event_id_source=event_id_source,
                    occurred_at_source=occurred_at_source,
                )
        self.assertEqual(self.source_calls, [])

    def test_fields_are_read_only(self) -> None:
        customer = self.make()
        for field, value in (
            ("id", CustomerId("customer-002")),
            ("name", CustomerName("Other Name")),
            ("address", CustomerAddress("Other Address")),
            ("city", CustomerCity("Surabaya")),
            ("notes", "other"),
        ):
            with self.subTest(field=field), self.assertRaises(AttributeError):
                setattr(customer, field, value)

    def test_each_unequal_update_records_exact_matching_event(self) -> None:
        customer = self.make("notes")
        customer.clear_events()
        new_name = CustomerName("Other Name")
        new_address = CustomerAddress("Other Address")
        new_city = CustomerCity("Surabaya")
        cases = (
            (customer.change_name, new_name, "name", CustomerNameChanged),
            (customer.change_address, new_address, "address", CustomerAddressChanged),
            (customer.change_city, new_city, "city", CustomerCityChanged),
            (customer.change_notes, "  new notes  ", "notes", CustomerNotesChanged),
        )
        for operation, value, field, event_type in cases:
            customer.clear_events()
            calls_before = len(self.source_calls)
            self.assertIsNone(operation(value))
            self.assertIs(getattr(customer, field), value)
            events = customer.pending_events()
            self.assertEqual(len(events), 1)
            self.assertIs(type(events[0]), event_type)
            self.assertEqual(
                self.source_calls[calls_before:],
                ["id", "occurred_at"],
            )

    def test_update_payloads_preserve_exact_previous_and_new_values(self) -> None:
        customer = self.make("notes")
        customer.clear_events()
        new_name = CustomerName("Other Name")
        new_address = CustomerAddress("Other Address")
        new_city = CustomerCity("Surabaya")
        new_notes = "  new notes  "
        customer.change_name(new_name)
        customer.change_address(new_address)
        customer.change_city(new_city)
        customer.change_notes(new_notes)
        name_event, address_event, city_event, notes_event = customer.pending_events()
        self.assertIs(name_event.previous_name, self.name)
        self.assertIs(name_event.new_name, new_name)
        self.assertIs(address_event.previous_address, self.address)
        self.assertIs(address_event.new_address, new_address)
        self.assertIs(city_event.previous_city, self.city)
        self.assertIs(city_event.new_city, new_city)
        self.assertIs(notes_event.previous_notes, "notes")
        self.assertIs(notes_event.new_notes, new_notes)
        for event in customer.pending_events():
            self.assertIs(event.customer_id, self.identity)

    def test_equal_updates_are_no_ops_without_source_or_event(self) -> None:
        customer = self.make("notes")
        customer.clear_events()
        calls_before = list(self.source_calls)
        original = (customer.name, customer.address, customer.city, customer.notes)
        for operation, value in (
            (customer.change_name, CustomerName("Customer One")),
            (customer.change_address, CustomerAddress("First Address")),
            (customer.change_city, CustomerCity("Mojokerto")),
            (customer.change_notes, "notes"),
        ):
            self.assertIsNone(operation(value))
        self.assertEqual(
            (customer.name, customer.address, customer.city, customer.notes),
            original,
        )
        self.assertEqual(customer.pending_events(), ())
        self.assertEqual(self.source_calls, calls_before)

    def test_invalid_updates_preserve_state_events_and_sources(self) -> None:
        customer = self.make("notes")
        before_state = (
            customer.id,
            customer.name,
            customer.address,
            customer.city,
            customer.notes,
        )
        before_events = customer.pending_events()
        before_calls = list(self.source_calls)
        cases = (
            (customer.change_name, None),
            (customer.change_name, "name"),
            (customer.change_address, None),
            (customer.change_address, "address"),
            (customer.change_city, None),
            (customer.change_city, "city"),
            (customer.change_notes, 1),
        )
        for operation, value in cases:
            with self.subTest(operation=operation.__name__), self.assertRaises(
                DomainValidationError
            ):
                operation(value)
            self.assertEqual(
                (
                    customer.id,
                    customer.name,
                    customer.address,
                    customer.city,
                    customer.notes,
                ),
                before_state,
            )
            self.assertEqual(customer.pending_events(), before_events)
            self.assertEqual(self.source_calls, before_calls)

    def test_metadata_and_factory_failures_are_atomic(self) -> None:
        failures = (
            lambda: (_ for _ in ()).throw(RuntimeError("id failed")),
            self.event_id_source,
        )
        for index, event_id_source in enumerate(failures):
            customer = self.make("notes")
            before_state = customer.name
            before_events = customer.pending_events()
            if index == 0:
                occurred_at_source = self.occurred_at_source
            else:
                occurred_at_source = lambda: (_ for _ in ()).throw(
                    RuntimeError("timestamp failed")
                )
            customer._event_id_source = event_id_source
            customer._occurred_at_source = occurred_at_source
            with self.subTest(index=index), self.assertRaises(RuntimeError):
                customer.change_name(CustomerName("Other Name"))
            self.assertIs(customer.name, before_state)
            self.assertEqual(customer.pending_events(), before_events)

        customer = self.make("notes")
        before_events = customer.pending_events()
        with patch.object(
            CustomerEventFactory,
            "create_customer_name_changed",
            side_effect=RuntimeError("factory failed"),
        ):
            with self.assertRaises(RuntimeError):
                customer.change_name(CustomerName("Other Name"))
        self.assertIs(customer.name, self.name)
        self.assertEqual(customer.pending_events(), before_events)

    def test_invalid_metadata_from_sources_is_atomic(self) -> None:
        customer = self.make("notes")
        before_events = customer.pending_events()
        customer._event_id_source = lambda: None
        with self.assertRaises(DomainValidationError):
            customer.change_name(CustomerName("Other Name"))
        self.assertIs(customer.name, self.name)
        self.assertEqual(customer.pending_events(), before_events)

        customer._event_id_source = self.event_id_source
        customer._occurred_at_source = lambda: datetime(2025, 1, 1)
        with self.assertRaises(DomainValidationError):
            customer.change_name(CustomerName("Other Name"))
        self.assertIs(customer.name, self.name)
        self.assertEqual(customer.pending_events(), before_events)

    def test_pending_pull_clear_and_operation_order(self) -> None:
        customer = self.make("notes")
        created_snapshot = customer.pending_events()
        self.assertIsInstance(created_snapshot, tuple)
        customer.change_name(CustomerName("Other Name"))
        customer.change_city(CustomerCity("Surabaya"))
        customer.change_notes(None)
        self.assertEqual(len(created_snapshot), 1)
        events = customer.pending_events()
        self.assertEqual(
            tuple(type(event) for event in events),
            (CustomerCreated, CustomerNameChanged, CustomerCityChanged, CustomerNotesChanged),
        )
        self.assertEqual(customer.pending_events(), events)
        pulled = customer.pull_events()
        self.assertEqual(pulled, events)
        self.assertEqual(customer.pending_events(), ())
        self.assertEqual(customer.pull_events(), ())
        self.assertIsNone(customer.clear_events())
        self.assertEqual(customer.pending_events(), ())
        self.assertEqual(customer.name, CustomerName("Other Name"))
        self.assertEqual(customer.city, CustomerCity("Surabaya"))
        self.assertIsNone(customer.notes)

    def test_pull_and_clear_do_not_recreate_customer_created(self) -> None:
        customer = self.make()
        self.assertIs(type(customer.pull_events()[0]), CustomerCreated)
        self.assertEqual(customer.pending_events(), ())
        customer.clear_events()
        self.assertEqual(customer.pending_events(), ())
        customer.change_notes("notes")
        self.assertEqual(
            tuple(type(event) for event in customer.pending_events()),
            (CustomerNotesChanged,),
        )

    def test_equal_event_instances_from_distinct_operations_are_retained(self) -> None:
        constant_time = datetime(2025, 2, 1, tzinfo=timezone.utc)
        customer = self.make(
            event_id_source=lambda: "same-event-id",
            occurred_at_source=lambda: constant_time,
        )
        other = CustomerName("Other Name")
        customer.change_name(other)
        customer.change_name(self.name)
        customer.change_name(other)
        events = customer.pending_events()
        self.assertEqual(events[1], events[3])
        self.assertIsNot(events[1], events[3])
        self.assertEqual(len(events), 4)

    def test_identity_equality_hashing_and_duplicates(self) -> None:
        def make(identity: CustomerId, name: CustomerName) -> Customer:
            return Customer(
                identity,
                name,
                self.address,
                self.city,
                event_id_source=self.event_id_source,
                occurred_at_source=self.occurred_at_source,
            )

        equal = make(CustomerId("customer-001"), CustomerName("Other Name"))
        other = make(CustomerId("customer-002"), self.name)
        current = self.make()
        self.assertEqual(current, equal)
        self.assertNotEqual(current, other)
        self.assertEqual(hash(current), hash(equal))
        self.assertEqual({current: "customer"}[equal], "customer")

    def test_published_api_and_package_exports_only(self) -> None:
        public = {name for name in vars(Customer) if not name.startswith("_")}
        self.assertEqual(
            public,
            {
                "name",
                "address",
                "city",
                "notes",
                "change_name",
                "change_address",
                "change_city",
                "change_notes",
            },
        )
        import core.domain.customer as package

        self.assertEqual(
            package.__all__,
            ("Customer", "CustomerId", "CustomerName", "CustomerAddress", "CustomerCity"),
        )

    def test_no_prohibited_dependencies_or_behavior(self) -> None:
        path = Path(__file__).parents[4] / "core/domain/customer/customer.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules = {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        names = {node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)}
        attributes = {
            node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        self.assertEqual(modules, {"collections", "datetime", "core"})
        self.assertTrue(
            {
                "uuid",
                "repository",
                "database",
                "persistence",
                "serialize",
                "json",
                "telegram",
                "eventenvelope",
            }.isdisjoint(names | attributes)
        )
        self.assertTrue(
            {"now", "utcnow", "time", "publish", "dispatch", "save"}.isdisjoint(
                attributes
            )
        )
        self.assertTrue(
            {
                "status",
                "delete",
                "deactivate",
                "archive",
                "merge",
                "restore",
                "created_at",
                "updated_at",
                "save",
                "find",
            }.isdisjoint(vars(Customer))
        )


if __name__ == "__main__":
    unittest.main()
