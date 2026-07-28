import unittest

from core.domain.exceptions import (
    DomainError,
    DomainInvariantError,
    DomainValidationError,
)


class DomainExceptionTests(unittest.TestCase):
    def test_domain_error_inherits_from_exception(self):
        self.assertTrue(issubclass(DomainError, Exception))

    def test_shared_exceptions_inherit_from_domain_error(self):
        exception_types = (DomainValidationError, DomainInvariantError)

        for exception_type in exception_types:
            with self.subTest(exception_type=exception_type):
                self.assertTrue(issubclass(exception_type, DomainError))

    def test_exception_messages_are_preserved(self):
        for exception_type in (
            DomainError,
            DomainValidationError,
            DomainInvariantError,
        ):
            with self.subTest(exception_type=exception_type):
                self.assertEqual(str(exception_type("message")), "message")


if __name__ == "__main__":
    unittest.main()
