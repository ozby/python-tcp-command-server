import unittest

from echo_server.request import Request
class TestParserInput(unittest.TestCase):
    def test_parse_commands(self) -> None:
        # Test SIGN_IN command
        self.assertEqual(
            vars(Request.fromLine("ougmcim|SIGN_IN|janedoe")),
            vars(Request(request_id="ougmcim", action="SIGN_IN", client_id="janedoe")),
        )

        self.assertEqual(
            vars(Request.fromLine("iwhygsi|WHOAMI")),
            vars(Request(request_id="iwhygsi", action="WHOAMI"))
        )

        self.assertEqual(
            vars(Request.fromLine("cadlsdo|SIGN_OUT")),
            vars(Request(request_id="cadlsdo", action="SIGN_OUT")),
        )

    def test_parse_failures(self) -> None:
        with self.assertRaises(ValueError):
            Request.fromLine("abc|SIGN_IN|janedoe")

        with self.assertRaises(ValueError):
            Request.fromLine("abc123d|SIGN_IN|janedoe")

        with self.assertRaises(ValueError):
            Request.fromLine("abcdefg")

        with self.assertRaises(ValueError):
            Request.fromLine("abcdefg|INVALID|janedoe")

        with self.assertRaises(ValueError):
            Request.fromLine("abcdefg|WHOAMI|janedoe")

        with self.assertRaises(ValueError):
            Request.fromLine("abcdefg|SIGN_OUT|janedoe")

        with self.assertRaises(ValueError):
            Request.fromLine("abcdefg|SIGN_IN")

        # New error cases for client_id validation
        with self.assertRaises(ValueError):
            Request.fromLine("abcdefg|SIGN_IN|invalid@id")  # non-alphanumeric client_id

        with self.assertRaises(ValueError):
            Request.fromLine("abcdefg|SIGN_IN|invalid id")  # space in client_id

        with self.assertRaises(ValueError):
            Request.fromLine("abcdefg|SIGN_IN|")  # empty client_id


if __name__ == "__main__":
    unittest.main(verbosity=2)
