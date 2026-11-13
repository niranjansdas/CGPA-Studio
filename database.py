
import sqlite3
import os
import sys
import shutil

from pathlib import Path
from contextlib import contextmanager
from datetime import datetime


class CGPADatabase:

    def __init__(self, database_name="cgpa_studio.db"):

        # Find the folder containing the application.
        if getattr(sys, "frozen", False):
            application_folder = Path(sys.executable).resolve().parent
        else:
            application_folder = Path(__file__).resolve().parent

        # Choose a suitable location for the database.
        if os.name == "nt":
            base_folder = Path(
                os.environ.get(
                    "LOCALAPPDATA",
                    Path.home() / "AppData" / "Local"
                )
            )
        else:
            base_folder = Path.home() / ".local" / "share"

        self.data_folder = base_folder / "CGPAStudio"
        self.data_folder.mkdir(parents=True, exist_ok=True)

        self.database_path = self.data_folder / database_name
        self.database_name = str(self.database_path)

        # Migrate an existing database on first run.
        old_database = application_folder / database_name

        if (
            not self.database_path.exists()
            and old_database.exists()
            and old_database.resolve() != self.database_path.resolve()
        ):
            shutil.copy2(old_database, self.database_path)

        self.create_tables()

    # DATABASE CONNECTION
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

    # CREATE A DATABASE BACKUP
    def create_backup(self, backup_path):

        backup_path = Path(backup_path)

        if backup_path.resolve() == self.database_path.resolve():
            raise ValueError(
                "Backup cannot overwrite the active database."
            )

        backup_path.parent.mkdir(parents=True, exist_ok=True)

        source = sqlite3.connect(self.database_name)
        destination = sqlite3.connect(str(backup_path))

        try:
            source.backup(destination)

        finally:
            destination.close()
            source.close()

        return str(backup_path)

    # RESTORE A DATABASE BACKUP
    def restore_backup(self, backup_path):

        backup_path = Path(backup_path)

        if not backup_path.is_file():
            raise FileNotFoundError("Backup file does not exist.")

        if backup_path.resolve() == self.database_path.resolve():
            raise ValueError(
                "Selected file is already the active database."
            )

        # Validate the selected backup.
        check = sqlite3.connect(
            f"file:{backup_path.resolve().as_posix()}?mode=ro",
            uri=True
        )

        try:

            integrity = check.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

            if integrity != "ok":
                raise ValueError(
                    "The selected database is damaged."
                )

            tables = {
                row[0]
                for row in check.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                """).fetchall()
            }

            if not {"semesters", "subjects"}.issubset(tables):
                raise ValueError(
                    "This is not a valid CGPA Studio database."
                )

            required_columns = {
                "semesters": {"id", "name"},
                "subjects": {
                    "id", "semester_id", "name",
                    "credits", "grade", "points"
                }
            }

            for table, expected_columns in required_columns.items():

                actual_columns = {
                    row[1]
                    for row in check.execute(
                        f"PRAGMA table_info({table})"
                    ).fetchall()
                }

                if not expected_columns.issubset(actual_columns):
                    raise ValueError(
                        "The selected database has an incompatible structure."
                    )

        finally:
            check.close()

        # Create a uniquely named safety backup of current data.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        safety_path = (
            self.data_folder /
            f"before_restore_{timestamp}.db"
        )

        current = sqlite3.connect(self.database_name)
        safety = sqlite3.connect(str(safety_path))

        try:
            current.backup(safety)

        finally:
            safety.close()
            current.close()

        # Restore the selected backup.
        source = sqlite3.connect(str(backup_path))
        destination = sqlite3.connect(self.database_name)

        try:
            source.backup(destination)

        finally:
            destination.close()
            source.close()

        return str(safety_path)
