
import sqlite3
from contextlib import contextmanager


class CGPADatabase:

    def __init__(self, database_name="cgpa_studio.db"):
        self.database_name = database_name
        self.create_tables()

    # CONNECT TO DATABASE
    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.database_name)
        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA foreign_keys = ON")

        try:
            yield conn
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    # CREATE DATABASE TABLES
    def create_tables(self):

        with self.connection() as conn:

            conn.execute("""
                CREATE TABLE IF NOT EXISTS semesters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    semester_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    credits REAL NOT NULL,
                    grade REAL NOT NULL,
                    points REAL NOT NULL,

                    FOREIGN KEY (semester_id)
                    REFERENCES semesters(id)
                    ON DELETE CASCADE
                )
            """)

            # Create Semester 1 if database is empty
            conn.execute("""
                INSERT OR IGNORE INTO semesters (name)
                VALUES ('Semester 1')
            """)

    # ADD A SEMESTER
    def add_semester(self, name):

        with self.connection() as conn:
            conn.execute("""
                INSERT INTO semesters (name)
                VALUES (?)
            """, (name,))

    # GET ALL SEMESTERS
    def get_semesters(self):

        with self.connection() as conn:
            rows = conn.execute("""
                SELECT name
                FROM semesters
                ORDER BY id
            """).fetchall()

            return [row["name"] for row in rows]

    # DELETE A SEMESTER
    def delete_semester(self, name):

        with self.connection() as conn:
            conn.execute("""
                DELETE FROM semesters
                WHERE name = ?
            """, (name,))

    # GET SUBJECTS OF A SEMESTER
    def get_subjects(self, semester_name):

        with self.connection() as conn:

            rows = conn.execute("""
                SELECT subjects.*
                FROM subjects
                JOIN semesters
                ON subjects.semester_id = semesters.id
                WHERE semesters.name = ?
            """, (semester_name,)).fetchall()

            subjects = {}

            for row in rows:
                subject_id = str(row["id"])

                subjects[subject_id] = {
                    "name": row["name"],
                    "credits": row["credits"],
                    "grade": row["grade"],
                    "points": row["points"]
                }

            return subjects

    # ADD A SUBJECT
    def add_subject(self, semester_name, name, credits, grade):

        points = credits * grade

        with self.connection() as conn:

            semester = conn.execute("""
                SELECT id
                FROM semesters
                WHERE name = ?
            """, (semester_name,)).fetchone()

            if semester is None:
                raise ValueError("Semester does not exist.")

            conn.execute("""
                INSERT INTO subjects
                (semester_id, name, credits, grade, points)
                VALUES (?, ?, ?, ?, ?)
            """, (
                semester["id"],
                name,
                credits,
                grade,
                points
            ))

    # UPDATE A SUBJECT
    def update_subject(self, subject_id, name, credits, grade):

        points = credits * grade

        with self.connection() as conn:
            conn.execute("""
                UPDATE subjects
                SET name = ?,
                    credits = ?,
                    grade = ?,
                    points = ?
                WHERE id = ?
            """, (
                name,
                credits,
                grade,
                points,
                int(subject_id)
            ))

    # DELETE A SUBJECT
    def delete_subject(self, subject_id):

        with self.connection() as conn:
            conn.execute("""
                DELETE FROM subjects
                WHERE id = ?
            """, (int(subject_id),))

    # CLEAR ALL SUBJECTS IN A SEMESTER
    def clear_semester(self, semester_name):

        with self.connection() as conn:
            conn.execute("""
                DELETE FROM subjects
                WHERE semester_id = (
                    SELECT id
                    FROM semesters
                    WHERE name = ?
                )
            """, (semester_name,))

    # GET ALL SUBJECTS FROM ALL SEMESTERS
    def get_all_subjects(self):

        with self.connection() as conn:

            rows = conn.execute("""
                SELECT
                    semesters.name AS semester,
                    subjects.name AS subject,
                    subjects.credits,
                    subjects.grade,
                    subjects.points
                FROM subjects
                JOIN semesters
                ON subjects.semester_id = semesters.id
                ORDER BY semesters.id, subjects.id
            """).fetchall()

            return [dict(row) for row in rows]
