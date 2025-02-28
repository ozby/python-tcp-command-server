import unittest

from server.request import Request
from server.services.session_service import SessionService
from tests.test_discussions import TEST_PEER_ID


class TestParserInput(unittest.TestCase):
    def test_parse_actions(self) -> None:
        SessionService().set(TEST_PEER_ID, "tester_client_1")
        # Test SIGN_IN action
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

        self.assertEqual(
            vars(
                Request.from_line(
                    'ykkngzx|CREATE_DISCUSSION|iofetzv.0s|Hey, folks. What do you think of my video? Does it have enough "polish"?',
                    TEST_PEER_ID,
                )
            ),
            vars(
                Request(
                    request_id="ykkngzx",
                    action="CREATE_DISCUSSION",
                    params=[
                        "iofetzv.0s",
                        'Hey, folks. What do you think of my video? Does it have enough "polish"?',
                    ],
                    peer_id=TEST_PEER_ID,
                )
            ),
        )

        self.assertEqual(
            vars(
                Request.from_line(
                    "sqahhfj|CREATE_REPLY|iztybsd|I think it's great!", TEST_PEER_ID
                )
            ),
            vars(
                Request(
                    request_id="sqahhfj",
                    action="CREATE_REPLY",
                    params=["iztybsd", "I think it's great!"],
                    peer_id=TEST_PEER_ID,
                )
            ),
        )

        self.assertEqual(
            vars(Request.from_line("xthbsuv|GET_DISCUSSION|iztybsd")),
            vars(
                Request(
                    request_id="xthbsuv", action="GET_DISCUSSION", params=["iztybsd"]
                )
            ),
        )

        self.assertEqual(
            vars(Request.from_line("xthbsuv|LIST_DISCUSSIONS")),
            vars(Request(request_id="xthbsuv", action="LIST_DISCUSSIONS", params=[])),
        )

        self.assertEqual(
            vars(Request.from_line("xthbsuv|LIST_DISCUSSIONS|refprefix")),
            vars(
                Request(
                    request_id="xthbsuv",
                    action="LIST_DISCUSSIONS",
                    params=["refprefix"],
                )
            ),
        )

    def test_parse_failures(self) -> None:
        with self.assertRaises(ValueError):
            Request.from_line("abc|SIGN_IN|janedoe")

        with self.assertRaises(ValueError):
            Request.from_line("abc123d|SIGN_IN|janedoe")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg")

        with self.assertRaises(ValueError):
            Request.from_line("cadlsdo|INVALID")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|SIGN_IN")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|SIGN_IN|invalid@id")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|SIGN_IN|invalid id")

        with self.assertRaises(ValueError):
            Request.from_line("abcdefg|SIGN_IN|")

        with self.assertRaises(ValueError):
            Request.from_line("ykkngzx|CREATE_DISCUSSION|iofetzv.0s")

        with self.assertRaises(ValueError):
            Request.from_line("ykkngzx|CREATE_DISCUSSION|iofetzv.0s|")

        with self.assertRaises(ValueError):
            Request.from_line("ykkngzx|CREATE_DISCUSSION|iofetzv|zaaa")


if __name__ == "__main__":
    unittest.main(verbosity=2)
