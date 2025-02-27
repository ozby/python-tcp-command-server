import unittest

from server.validation import Validator


class TestValidator(unittest.TestCase):
    def test_validate_request_id(self) -> None:
        self.assertTrue(Validator.validate_request_id("abcdefg"))

        self.assertFalse(Validator.validate_request_id("abc"))  # too short
        self.assertFalse(Validator.validate_request_id("abcdefgh"))  # too long
        self.assertFalse(Validator.validate_request_id("ABCDEFG"))
        self.assertFalse(Validator.validate_request_id("abc123"))  # numbers not allowed

    def test_validate_client_id(self) -> None:
        self.assertTrue(Validator.validate_client_id("janedoe"))
        self.assertTrue(Validator.validate_client_id("jane123"))
        self.assertTrue(Validator.validate_client_id("JANE123"))

        self.assertFalse(Validator.validate_client_id("jane@doe"))
        self.assertFalse(Validator.validate_client_id("jane doe"))  # spaces not allowed
        self.assertFalse(Validator.validate_client_id(""))  # empty not allowed


if __name__ == "__main__":
    unittest.main()
