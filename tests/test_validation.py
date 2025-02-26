import unittest

from echo_server.validation import Validator


class TestValidator(unittest.TestCase):
    def test_validate_request_id(self) -> None:
        # Test valid request_id
        self.assertTrue(Validator.validate_request_id("abcdefg"))

        # Test invalid request_ids
        self.assertFalse(Validator.validate_request_id("abc"))  # too short
        self.assertFalse(Validator.validate_request_id("abcdefgh"))  # too long
        self.assertFalse(Validator.validate_request_id("ABCDEFG"))  # uppercase not allowed
        self.assertFalse(Validator.validate_request_id("abc123"))  # numbers not allowed

    def test_validate_client_id(self) -> None:
        # Test valid client_ids
        self.assertTrue(Validator.validate_client_id("janedoe"))
        self.assertTrue(Validator.validate_client_id("jane123"))
        self.assertTrue(Validator.validate_client_id("JANE123"))

        # Test invalid client_ids
        self.assertFalse(Validator.validate_client_id("jane@doe"))  # special chars not allowed
        self.assertFalse(Validator.validate_client_id("jane doe"))  # spaces not allowed
        self.assertFalse(Validator.validate_client_id(""))  # empty not allowed


if __name__ == "__main__":
    unittest.main() 