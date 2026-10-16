"""FastAPI routes for creating, reading, updating and deleting students."""
import sqlite3
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status

from app.database import get_connection, init_db
from app.schemas import StudentCreate, StudentResponse, StudentUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when the API starts. The table is created only if it is missing.
    init_db()
    yield


app = FastAPI(
    title="Students Database CRUD API",
    description="A beginner-friendly student records API built with FastAPI and SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a SQLite row into a normal dictionary for the response."""
    return dict(row)


def fetch_student(student_id: int) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return row_to_dict(row)


@app.get("/", tags=["General"])
def home():
    return {"message": "Students Database CRUD API is running", "docs": "/docs"}


@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentCreate):
    data = student.model_dump()
    # SQLite stores dates as ISO-formatted text (YYYY-MM-DD).
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """INSERT INTO students
                (name, date_of_birth, email, phone, course, address, enrollment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["name"], data["date_of_birth"], data["email"], data["phone"],
                 data["course"], data["address"], data["enrollment_date"]),
            )
            student_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        if "students.email" in str(exc) or "UNIQUE constraint failed" in str(exc):
            raise HTTPException(status_code=409, detail="A student with this email already exists") from exc
        raise HTTPException(status_code=400, detail="Could not create student") from exc
    return fetch_student(student_id)


@app.get("/students", response_model=list[StudentResponse], tags=["Students"])
def list_students(
    name: Optional[str] = Query(default=None, description="Find names containing this text"),
    course: Optional[str] = Query(default=None, description="Filter by course"),
    born_after: Optional[date] = Query(default=None, description="Date of birth after this date"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    sql = "SELECT * FROM students WHERE 1=1"
    parameters: list = []
    if name:
        sql += " AND name LIKE ? COLLATE NOCASE"
        parameters.append(f"%{name.strip()}%")
    if course:
        sql += " AND course = ? COLLATE NOCASE"
        parameters.append(course.strip())
    if born_after:
        sql += " AND date_of_birth > ?"
        parameters.append(born_after.isoformat())
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    parameters.extend([limit, offset])
    with get_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [row_to_dict(row) for row in rows]


@app.get("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def get_student(student_id: int):
    return fetch_student(student_id)


@app.put("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def replace_student(student_id: int, student: StudentCreate):
    """Replace all editable student fields; required fields must be supplied."""
    fetch_student(student_id)  # Return 404 before attempting the update.
    data = student.model_dump()
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()
    try:
        with get_connection() as connection:
            connection.execute(
                """UPDATE students SET name=?, date_of_birth=?, email=?, phone=?,
                course=?, address=?, enrollment_date=? WHERE id=?""",
                (data["name"], data["date_of_birth"], data["email"], data["phone"],
                 data["course"], data["address"], data["enrollment_date"], student_id),
            )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="A student with this email already exists") from exc
    return fetch_student(student_id)


@app.patch("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def update_student(student_id: int, student: StudentUpdate):
    """Update only fields included in the request body."""
    existing = fetch_student(student_id)
    changes = student.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")
    # Do not allow a PATCH to remove the only contact method.
    resulting_email = changes.get("email", existing["email"])
    resulting_phone = changes.get("phone", existing["phone"])
    if not resulting_email and not resulting_phone:
        raise HTTPException(status_code=422, detail="A student must have an email address or phone number")
    for key, value in changes.items():
        if isinstance(value, date):
            changes[key] = value.isoformat()
    columns = ", ".join(f"{column} = ?" for column in changes)
    values = list(changes.values()) + [student_id]
    try:
        with get_connection() as connection:
            connection.execute(f"UPDATE students SET {columns} WHERE id = ?", values)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="A student with this email already exists") from exc
    return fetch_student(student_id)


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: int):
    fetch_student(student_id)
    with get_connection() as connection:
        connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
