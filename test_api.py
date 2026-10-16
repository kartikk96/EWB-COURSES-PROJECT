"""Basic automated tests. Tests use a temporary SQLite database."""
import os
import tempfile
import unittest
from fastapi.testclient import TestClient

# Set the DB path before importing the app/database module.
_temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_temp_db.close()
os.environ["DATABASE_PATH"] = _temp_db.name

from app.main import app  # noqa: E402


class StudentApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Explicitly initialize the test database before each test.
        from app.database import get_connection, init_db
        init_db()
        with get_connection() as connection:
            connection.execute("DELETE FROM students")

    def tearDown(self):
        self.client.close()

    def sample_student(self):
        return {
            "name": "Aarav Sharma",
            "date_of_birth": "2005-04-12",
            "email": "aarav.test@example.com",
            "phone": "9876543210",
            "course": "B.Tech CSE",
            "address": "Bhimtal",
            "enrollment_date": "2024-08-01",
        }

    def test_crud_flow(self):
        created = self.client.post("/students", json=self.sample_student())
        self.assertEqual(created.status_code, 201)
        student_id = created.json()["id"]
        self.assertEqual(self.client.get(f"/students/{student_id}").status_code, 200)
        patched = self.client.patch(f"/students/{student_id}", json={"course": "CSE"})
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(patched.json()["course"], "CSE")
        self.assertEqual(self.client.delete(f"/students/{student_id}").status_code, 204)
        self.assertEqual(self.client.get(f"/students/{student_id}").status_code, 404)

    def test_validation_requires_contact(self):
        student = self.sample_student()
        student["email"] = None
        student["phone"] = None
        self.assertEqual(self.client.post("/students", json=student).status_code, 422)

    def test_duplicate_email_rejected(self):
        self.client.post("/students", json=self.sample_student())
        second = self.sample_student()
        second["name"] = "Another Student"
        self.assertEqual(self.client.post("/students", json=second).status_code, 409)

    def test_name_filter(self):
        self.client.post("/students", json=self.sample_student())
        response = self.client.get("/students", params={"name": "aarav"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)


if __name__ == "__main__":
    unittest.main()
