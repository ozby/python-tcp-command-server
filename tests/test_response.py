import unittest

from echo_server.response import Response, ResponseGenerator


class TestResponseGenerator(unittest.TestCase):
    def test_serialize_response(self) -> None:
        # Test response with only request_id
        result = ResponseGenerator.serialize(
            Response(request_id="abcdefg")
        )
        self.assertEqual(result, "abcdefg")

        # Test response with request_id and client_id
        result = ResponseGenerator.serialize(
            Response(request_id="abcdefg", client_id="janedoe")
        )
        self.assertEqual(result, "abcdefg|janedoe")

    def test_serialize_failures(self) -> None:
        # Test invalid request_id
        with self.assertRaises(ValueError):
            ResponseGenerator.serialize(Response(request_id="abc"))  # too short

        with self.assertRaises(ValueError):
            ResponseGenerator.serialize(Response(request_id="abc123d"))  # contains numbers

        with self.assertRaises(ValueError):
            ResponseGenerator.serialize(Response(request_id="ABCDEFG"))  # uppercase

        # Test invalid client_id
        with self.assertRaises(ValueError):
            ResponseGenerator.serialize(
                Response(request_id="abcdefg", client_id="invalid@id")
            )  # special chars

        with self.assertRaises(ValueError):
            ResponseGenerator.serialize(
                Response(request_id="abcdefg", client_id="invalid id")
            )  # spaces


if __name__ == "__main__":
    unittest.main() 