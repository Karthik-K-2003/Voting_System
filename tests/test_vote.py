import unittest
import json
from app import app


class VoteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # 1. Not logged in
    def test_vote_not_logged_in(self):
        response = self.app.post("/vote", json={"participant_id": "123"})
        data = json.loads(response.data)

        self.assertEqual(data["status"], "error")
        self.assertIn("Login", data["message"])

    # 2. Missing participant_id
    def test_vote_missing_participant(self):
        with self.app.session_transaction() as sess:
            sess["user_id"] = "test_user"

        response = self.app.post("/vote", json={})
        data = json.loads(response.data)

        self.assertEqual(data["status"], "error")
        self.assertIn("Invalid", data["message"])

    # 3. Already voted
    def test_vote_already_voted(self):
        with self.app.session_transaction() as sess:
            sess["user_id"] = "test_user"

        # First vote (assume works)
        self.app.post("/vote", json={"participant_id": "p1"})

        # Second vote
        response = self.app.post("/vote", json={"participant_id": "p1"})
        data = json.loads(response.data)

        self.assertEqual(data["status"], "error")
        self.assertIn("already", data["message"])

    # 4. Successful vote
    def test_vote_success(self):
        with self.app.session_transaction() as sess:
            sess["user_id"] = "new_user"

        response = self.app.post("/vote", json={"participant_id": "p1"})
        data = json.loads(response.data)

        self.assertEqual(data["status"], "success")

    # 5. Invalid participant
    def test_vote_invalid_participant(self):
        with self.app.session_transaction() as sess:
            sess["user_id"] = "another_user"

        response = self.app.post("/vote", json={"participant_id": None})
        data = json.loads(response.data)

        self.assertEqual(data["status"], "error")


if __name__ == "__main__":
    unittest.main()
