import unittest

from echo_server.response import Response


class TestResponse(unittest.TestCase):
    def test_serialize_response(self) -> None:
        result = Response(request_id="abcdefg").serialize()
        self.assertEqual(result, "abcdefg\n")

        result = Response(request_id="abcdefg", params=["janedoe"]).serialize()
        self.assertEqual(result, "abcdefg|janedoe\n")

    def test_serialize_failures(self) -> None:
        with self.assertRaises(ValueError):
            Response(request_id="abc").serialize()

        with self.assertRaises(ValueError):
            Response(request_id="abc123d").serialize()

        with self.assertRaises(ValueError):
            Response(request_id="ABCDEFG").serialize()


if __name__ == "__main__":
    unittest.main(verbosity=2)
