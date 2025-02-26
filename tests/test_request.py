import unittest

from echo_server.request import Command, RequestParser


class TestParserInput(unittest.TestCase):
    def test_parse_commands(self) -> None:
        # Test SIGN_IN command
        result = RequestParser.parse("ougmcim|SIGN_IN|janedoe")
        self.assertEqual(
            result,
            Command(request_id="ougmcim", action="SIGN_IN", client_id="janedoe"),
        )

        # Test WHOAMI command
        result = RequestParser.parse("iwhygsi|WHOAMI")
        self.assertEqual(
            result, Command(request_id="iwhygsi", action="WHOAMI", client_id=None)
        )

        # Test SIGN_OUT command
        result = RequestParser.parse("cadlsdo|SIGN_OUT")
        self.assertEqual(
            result,
            Command(request_id="cadlsdo", action="SIGN_OUT", client_id=None),
        )

    def test_parse_failures(self) -> None:
        with self.assertRaises(ValueError):
            RequestParser.parse("abc|SIGN_IN|janedoe")

        with self.assertRaises(ValueError):
            RequestParser.parse("abc123d|SIGN_IN|janedoe")

        with self.assertRaises(ValueError):
            RequestParser.parse("abcdefg")

        with self.assertRaises(ValueError):
            RequestParser.parse("abcdefg|INVALID|janedoe")

        with self.assertRaises(ValueError):
            RequestParser.parse("abcdefg|WHOAMI|janedoe")

        with self.assertRaises(ValueError):
            RequestParser.parse("abcdefg|SIGN_OUT|janedoe")

        with self.assertRaises(ValueError):
            RequestParser.parse("abcdefg|SIGN_IN")

        # New error cases for client_id validation
        with self.assertRaises(ValueError):
            RequestParser.parse("abcdefg|SIGN_IN|invalid@id")  # non-alphanumeric client_id

        with self.assertRaises(ValueError):
            RequestParser.parse("abcdefg|SIGN_IN|invalid id")  # space in client_id

        with self.assertRaises(ValueError):
            RequestParser.parse("abcdefg|SIGN_IN|")  # empty client_id

    def test_validation_methods(self) -> None:
        # Test request_id validation
        self.assertTrue(RequestParser.validate_request_id("abcdefg"))
        self.assertFalse(RequestParser.validate_request_id("abc"))  # too short
        self.assertFalse(RequestParser.validate_request_id("abcdefgh"))  # too long
        self.assertFalse(RequestParser.validate_request_id("ABCDEFG"))  # uppercase not allowed
        self.assertFalse(RequestParser.validate_request_id("abc123"))  # numbers not allowed

        # Test client_id validation
        self.assertTrue(RequestParser.validate_client_id("janedoe"))
        self.assertTrue(RequestParser.validate_client_id("jane123"))
        self.assertTrue(RequestParser.validate_client_id("JANE123"))
        self.assertFalse(RequestParser.validate_client_id("jane@doe"))  # special chars not allowed
        self.assertFalse(RequestParser.validate_client_id("jane doe"))  # spaces not allowed


if __name__ == "__main__":
    unittest.main()
