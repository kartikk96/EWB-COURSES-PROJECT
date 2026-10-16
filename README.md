# Students Database CRUD API

A beginner-friendly Python backend project for the EWB Edu Tech internship assignment. It uses **FastAPI** to expose API endpoints and **SQLite** to store student records permanently on your computer.

## 1. Features

- Create, list, search, retrieve, update, and delete student records.
- Required fields: name and date of birth.
- Contact information: email and/or phone (at least one is required).
- Optional fields: course, address, enrollment date.
- Automatic unique integer student ID.
- Input validation, duplicate-email handling, and clear 404 errors.
- Search/filter by name, course, or date of birth; pagination with `limit` and `offset`.
- Interactive API documentation at `/docs`.
- Automated tests for the main CRUD flow and validation.

The optional Ollama AI extension is deliberately not included: the assignment says it is optional, and the mandatory CRUD application should work first.

## 2. Prerequisites

- Python 3.10 or newer (Python 3.11 is a good choice).
- Internet access to install the Python packages once.
- A terminal, Command Prompt, or VS Code terminal.

Check Python:

```bash
python --version
```

On some Windows installations, use `py --version` instead.

## 3. Install and run

Open a terminal in this project folder (the folder containing `requirements.txt`).

### Windows PowerShell / Command Prompt

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

If `python` does not work, try `py` in the commands. In PowerShell, if script activation is blocked, use Command Prompt or run the environment's Python directly: `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m uvicorn app.main:app --reload`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

When the server starts, open:

- API home: http://127.0.0.1:8000/
- Interactive API docs: http://127.0.0.1:8000/docs

Stop the server with `Ctrl+C`. SQLite creates `students.db` in the project root automatically when the application starts. Do not commit that database if it contains personal information.

## 4. Test the API using the browser

1. Start the server.
2. Open http://127.0.0.1:8000/docs.
3. Expand an endpoint, click **Try it out**, enter a request body if required, and click **Execute**.
4. Create a student before trying get/update/delete. Use the returned `id` in the URL.

Example request body (use dummy information only):

```json
{
  "name": "Aarav Sharma",
  "date_of_birth": "2005-04-12",
  "email": "aarav.demo@example.com",
  "phone": "9876543210",
  "course": "B.Tech CSE",
  "address": "Bhimtal",
  "enrollment_date": "2024-08-01"
}
```

Dates must use `YYYY-MM-DD`. Email or phone is required; both are allowed. Email addresses must be unique.

## 5. Endpoints

| Method | Endpoint | Purpose | Expected success |
|---|---|---|---|
| GET | `/` | Check that the API is running | 200 |
| POST | `/students` | Create a student | 201 |
| GET | `/students` | List students | 200 |
| GET | `/students?name=aarav` | Search names | 200 |
| GET | `/students?course=B.Tech%20CSE` | Filter by course | 200 |
| GET | `/students?born_after=2005-01-01` | Students born after a date | 200 |
| GET | `/students?limit=20&offset=0` | Paginated list | 200 |
| GET | `/students/1` | Retrieve one student | 200, or 404 if missing |
| PUT | `/students/1` | Replace all editable fields | 200 |
| PATCH | `/students/1` | Update only supplied fields | 200 |
| DELETE | `/students/1` | Delete a student | 204 |

The example ID `1` is illustrative; use an ID returned by your own API.

## 6. Optional command-line examples

These use `curl`, which is available in many terminals. In PowerShell, `curl` may be an alias on older versions; use the Swagger page if these commands behave differently.

Create:

```bash
curl -X POST http://127.0.0.1:8000/students -H "Content-Type: application/json" -d '{"name":"Aarav Sharma","date_of_birth":"2005-04-12","email":"aarav.demo@example.com","course":"B.Tech CSE"}'
```

List:

```bash
curl http://127.0.0.1:8000/students
```

Search:

```bash
curl "http://127.0.0.1:8000/students?name=Aarav"
```

Update only the course (replace `1` with the real ID):

```bash
curl -X PATCH http://127.0.0.1:8000/students/1 -H "Content-Type: application/json" -d '{"course":"Computer Science"}'
```

Delete (replace `1` with the real ID):

```bash
curl -X DELETE http://127.0.0.1:8000/students/1
```

## 7. Run the tests

With the virtual environment activated and dependencies installed:

```bash
python -m unittest discover -s tests -v
```

The tests use a temporary database path so they do not modify your regular `students.db` file.

## 8. Project structure

```text
ewb_students_crud/
├── app/
│   ├── __init__.py
│   ├── database.py    # SQLite connection and table creation
│   ├── main.py        # FastAPI application and endpoint functions
│   └── schemas.py     # Input validation and response shapes
├── tests/
│   └── test_api.py    # Automated tests
├── .gitignore
├── requirements.txt
└── README.md
```

## 9. Beginner explanation

- **FastAPI** receives HTTP requests and maps them to Python functions. It also generates the `/docs` page.
- **SQLite** is a small database stored in a local file. The database remains after the server stops.
- **CRUD** means Create, Read, Update, Delete.
- **Pydantic schemas** in `schemas.py` check that request data has the expected fields and types before the endpoint uses it.
- **Parameterized SQL** uses `?` placeholders for values, rather than inserting user text directly into SQL. This helps prevent SQL injection.
- **`database.py`** opens the database and creates the table when the app starts.
- **`main.py`** defines the API routes and translates missing records or duplicate emails into useful HTTP errors.
- **`tests/test_api.py`** checks the core flow automatically.

## 10. Common HTTP status codes

- `200 OK`: a read or update succeeded.
- `201 Created`: a new student was created.
- `204 No Content`: a student was deleted successfully.
- `400 Bad Request`: a request cannot be processed as sent.
- `404 Not Found`: the requested student ID does not exist.
- `409 Conflict`: an email address is already used by another student.
- `422 Unprocessable Entity`: request validation failed, such as an invalid date or missing contact details.

## 11. GitHub submission

1. Create a new **public or trainer-approved private** GitHub repository, for example `ewb-students-crud-api`.
2. Extract this project ZIP and open the project folder in VS Code.
3. Check `.gitignore` is present. It excludes the local database and virtual environment.
4. Run the app and tests before uploading.
5. In the terminal, run:

```bash
git init
git add .
git commit -m "Build student CRUD API with FastAPI and SQLite"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ewb-students-crud-api.git
git push -u origin main
```

Replace the URL with your actual repository URL. Never upload real student data, passwords, API keys, or secrets. Submit the repository link through the channel announced by your EWB trainer.

## 12. Suggested demo order

1. Show `/docs` and explain that FastAPI generated it.
2. Create a dummy student and point out the returned ID.
3. List all students and filter by name/course.
4. Retrieve that student by ID.
5. PATCH one field and show that the other fields remain unchanged.
6. PUT a complete replacement record if desired.
7. Delete the record and show that a later GET returns 404.
8. Explain where SQLite stores records and show the tests passing.

**Privacy note:** Use only dummy data for your demonstration. This is an internship learning project, not a production system for storing real student personal information.
