import unittest

from core.specialists.shoegabox.customer import (
    CustomerDraft,
    CustomerValidationError,
)


class CustomerDraftTests(unittest.TestCase):
    def test_new_draft_is_incomplete(self):
        customer = CustomerDraft()

        self.assertFalse(customer.is_complete)
        self.assertEqual(
            customer.missing_fields(),
            ("name", "address", "city"),
        )

    def test_customer_can_be_completed(self):
        customer = CustomerDraft()

        customer.set_name("  PT   Maju Jaya ")
        customer.set_address(" Jalan Merdeka 10 ")
        customer.set_city(" Mojokerto ")
        customer.set_notes(" Pelanggan reseller ")

        self.assertTrue(customer.is_complete)
        self.assertEqual(customer.name, "PT Maju Jaya")
        self.assertEqual(customer.address, "Jalan Merdeka 10")
        self.assertEqual(customer.city, "Mojokerto")
        self.assertEqual(customer.notes, "Pelanggan reseller")

    def test_short_name_is_rejected(self):
        customer = CustomerDraft()

        with self.assertRaises(CustomerValidationError):
            customer.set_name("A")

    def test_short_address_is_rejected(self):
        customer = CustomerDraft()

        with self.assertRaises(CustomerValidationError):
            customer.set_address("Jln")

    def test_short_city_is_rejected(self):
        customer = CustomerDraft()

        with self.assertRaises(CustomerValidationError):
            customer.set_city("M")

    def test_to_dict_requires_complete_customer(self):
        customer = CustomerDraft()
        customer.set_name("Toko Berkah")

        with self.assertRaises(CustomerValidationError):
            customer.to_dict()

    def test_complete_customer_can_be_serialized(self):
        customer = CustomerDraft()
        customer.set_name("Toko Berkah")
        customer.set_address("Jalan Raya 20")
        customer.set_city("Mojokerto")

        data = customer.to_dict()

        self.assertEqual(data["name"], "Toko Berkah")
        self.assertEqual(data["city"], "Mojokerto")
        self.assertEqual(data["notes"], "")

    def test_confirmation_text_contains_customer_data(self):
        customer = CustomerDraft()
        customer.set_name("Toko Berkah")
        customer.set_address("Jalan Raya 20")
        customer.set_city("Mojokerto")

        confirmation = customer.confirmation_text()

        self.assertIn("Toko Berkah", confirmation)
        self.assertIn("Jalan Raya 20", confirmation)
        self.assertIn("Mojokerto", confirmation)
        self.assertIn("Ya / Tidak", confirmation)


if __name__ == "__main__":
    unittest.main()
