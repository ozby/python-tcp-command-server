import unittest

from echo_server.response import Response


class TestResponse(unittest.TestCase):
    def test_serialize_response(self) -> None:
        result = Response(request_id="abcdefg").serialize()
        self.assertEqual(result, "abcdefg\n")

        result = Response(request_id="abcdefg", client_id="janedoe").serialize()
        self.assertEqual(result, "abcdefg|janedoe\n")

    def test_serialize_failures(self) -> None:
        # Test invalid request_id
        with self.assertRaises(ValueError):
            Response(request_id="abc").serialize()

        with self.assertRaises(ValueError):
            Response(request_id="abc123d").serialize()

        with self.assertRaises(ValueError):
            Response(request_id="ABCDEFG").serialize()

        with self.assertRaises(ValueError):
            Response(request_id="abcdefg", client_id="invalid@id").serialize()

        with self.assertRaises(ValueError):
            Response(request_id="abcdefg", client_id="invalid id").serialize()


if __name__ == "__main__":
    unittest.main(verbosity=2) 