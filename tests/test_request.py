import unittest

from echo_server.request import Request


class TestParserInput(unittest.TestCase):
    def test_parse_commands(self) -> None:
        # Test SIGN_IN command
        self.assertEqual(
            vars(Request.from_line("ougmcim|SIGN_IN|janedoe")),
            vars(Request(request_id="ougmcim", action="SIGN_IN", params=["janedoe"])),
        )

        self.assertEqual(
            vars(Request.from_line("iwhygsi|WHOAMI")),
            vars(Request(request_id="iwhygsi", action="WHOAMI")),
        )

        self.assertEqual(
            vars(Request.from_line("cadlsdo|SIGN_OUT")),
            vars(Request(request_id="cadlsdo", action="SIGN_OUT")),
        )

        self.assertEqual(
            vars(Request.from_line("cadlsdo|SIGN_OUT")),
            vars(Request(request_id="cadlsdo", action="SIGN_OUT")),
        )

    def test_parse_failures(self) -> None:
        with self.assertRaises(ValueError):
            Request.from_line("abc|SIGN_IN|janedoe")

        with self.assertRaises(ValueError):
            Request.from_line("abc123d|SIGN_IN|janedoe")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|INVALID|janedoe")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|WHOAMI|janedoe")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|SIGN_OUT|janedoe")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|SIGN_IN")

        with self.assertRaises(ValueError):
            Request.from_line(
                "abcdefg|SIGN_IN|invalid@id"
            )

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|SIGN_IN|invalid id")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|SIGN_IN|")


if __name__ == "__main__":
    unittest.main(verbosity=2)
