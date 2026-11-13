
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

from database import CGPADatabase


class CGPAStudio:

    def __init__(self, root):
        self.root = root
        self.root.title("CGPA Studio | Version 0.4")
        self.root.geometry("1050x720")
        self.root.minsize(850, 600)
        self.root.configure(bg="#101827")

        # CONNECT TO DATABASE
        self.db = CGPADatabase()

        # LOAD EXISTING SEMESTERS
        self.semesters = self.db.get_semesters()
        self.current_semester = self.semesters[0]
        self.subjects = self.db.get_subjects(self.current_semester)

        self.editing_id = None

        self.create_interface()
        self.refresh_table()

    # CREATE INTERFACE
    def create_interface(self):

        # HEADER
        header = tk.Frame(self.root, bg="#101827")
        header.pack(fill="x", pady=(12, 5))

        tk.Label(
            header,
            text="CGPA STUDIO",
            font=("Arial", 25, "bold"),
            fg="white",
            bg="#101827"
        ).pack()

        tk.Label(
            header,
            text="Academic Performance Manager | Version 0.4",
            font=("Arial", 10),
            fg="#9CA3AF",
            bg="#101827"
        ).pack()

        # RESULT CARDS
        cards = tk.Frame(self.root, bg="#101827")
        cards.pack(fill="x", padx=25, pady=10)

        sgpa_card = tk.Frame(
            cards, bg="#1E3A5F", padx=15, pady=10
        )
        sgpa_card.pack(
            side="left", fill="both", expand=True, padx=(0, 6)
        )

        tk.Label(
            sgpa_card,
            text="CURRENT SEMESTER SGPA",
            font=("Arial", 10, "bold"),
            fg="#BFDBFE",
            bg="#1E3A5F"
        ).pack()

        self.sgpa_label = tk.Label(
            sgpa_card,
            text="--",
            font=("Arial", 25, "bold"),
            fg="white",
            bg="#1E3A5F"
        )
        self.sgpa_label.pack()

        cgpa_card = tk.Frame(
            cards, bg="#174B3A", padx=15, pady=10
        )
        cgpa_card.pack(
            side="left", fill="both", expand=True, padx=(6, 0)
        )

        tk.Label(
            cgpa_card,
            text="CUMULATIVE CGPA",
            font=("Arial", 10, "bold"),
            fg="#BBF7D0",
            bg="#174B3A"
        ).pack()

        self.cgpa_label = tk.Label(
            cgpa_card,
            text="--",
            font=("Arial", 25, "bold"),
            fg="white",
            bg="#174B3A"
        )
        self.cgpa_label.pack()

        # SEMESTER CONTROLS
        semester_frame = tk.Frame(
            self.root, bg="#1F2937", padx=12, pady=10
        )
        semester_frame.pack(fill="x", padx=25, pady=5)

        tk.Label(
            semester_frame,
            text="SELECT SEMESTER",
            font=("Arial", 9, "bold"),
            fg="white",
            bg="#1F2937"
        ).pack(side="left", padx=(0, 10))

        self.semester_var = tk.StringVar(
            value=self.current_semester
        )

        self.semester_dropdown = ttk.Combobox(
            semester_frame,
            textvariable=self.semester_var,
            state="readonly",
            width=18
        )
        self.semester_dropdown.pack(side="left", padx=5)
        self.semester_dropdown.bind(
            "<<ComboboxSelected>>", self.switch_semester
        )

        tk.Button(
            semester_frame,
            text="+ Add Semester",
            command=self.add_semester,
            bg="#2563EB",
            fg="white",
            padx=10
        ).pack(side="left", padx=5)

        tk.Button(
            semester_frame,
            text="Delete Semester",
            command=self.delete_semester,
            bg="#B91C1C",
            fg="white",
            padx=10
        ).pack(side="left", padx=5)

        self.update_semester_dropdown()

        # SUBJECT INPUT
        input_frame = tk.Frame(
            self.root, bg="#1F2937", padx=12, pady=10
        )
        input_frame.pack(fill="x", padx=25, pady=8)

        labels = ["Subject", "Credits", "Grade Point"]

        for column, label in enumerate(labels):
            tk.Label(
                input_frame,
                text=label,
                fg="white",
                bg="#1F2937"
            ).grid(row=0, column=column, padx=8)

        self.subject_entry = tk.Entry(input_frame, width=25)
        self.credit_entry = tk.Entry(input_frame, width=11)
        self.grade_entry = tk.Entry(input_frame, width=11)

        self.subject_entry.grid(
            row=1, column=0, padx=8, pady=7
        )
        self.credit_entry.grid(
            row=1, column=1, padx=8, pady=7
        )
        self.grade_entry.grid(
            row=1, column=2, padx=8, pady=7
        )

        self.action_button = tk.Button(
            input_frame,
            text="Add Subject",
            command=self.add_subject,
            bg="#2563EB",
            fg="white",
            padx=12
        )
        self.action_button.grid(row=1, column=3, padx=8)

        self.cancel_button = tk.Button(
            input_frame,
            text="Cancel Edit",
            command=self.cancel_edit,
            bg="#6B7280",
            fg="white",
            padx=10
        )
        self.cancel_button.grid(row=1, column=4, padx=8)
        self.cancel_button.grid_remove()

        # SUBJECT TABLE
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#1F2937",
            foreground="white",
            fieldbackground="#1F2937",
            rowheight=27
        )

        style.configure(
            "Treeview.Heading",
            background="#374151",
            foreground="white"
        )

        style.map(
            "Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "white")]
        )

        self.table = ttk.Treeview(
            self.root,
            columns=("subject", "credits", "grade", "points"),
            show="headings",
            height=9
        )

        self.table.heading("subject", text="Subject")
        self.table.heading("credits", text="Credits")
        self.table.heading("grade", text="Grade Point")
        self.table.heading("points", text="Weighted Points")

        self.table.column("subject", width=380)
        self.table.column("credits", width=130, anchor="center")
        self.table.column("grade", width=150, anchor="center")
        self.table.column("points", width=170, anchor="center")

        self.table.pack(
            fill="both", expand=True, padx=25, pady=5
        )

        # SUBJECT MANAGEMENT BUTTONS
        button_frame = tk.Frame(self.root, bg="#101827")
        button_frame.pack(pady=10)

        buttons = [
            ("Edit Selected", self.edit_subject, "#D97706"),
            ("Delete Selected", self.delete_subject, "#DC2626"),
            ("Clear Semester", self.clear_semester, "#6B7280"),
            ("Database Status", self.save_semester, "#059669")
        ]

        for label, command, color in buttons:
            tk.Button(
                button_frame,
                text=label,
                command=command,
                bg=color,
                fg="white",
                padx=12
            ).pack(side="left", padx=5)

        self.status_label = tk.Label(
            self.root,
            text="All changes are automatically saved to the database.",
            font=("Arial", 9),
            fg="#86EFAC",
            bg="#101827"
        )
        self.status_label.pack(pady=(0, 8))

    # UPDATE SEMESTER DROPDOWN
    def update_semester_dropdown(self):
        self.semester_dropdown["values"] = self.semesters
        self.semester_var.set(self.current_semester)

    # RELOAD CURRENT SEMESTER FROM DATABASE
    def load_current_semester(self):
        self.subjects = self.db.get_subjects(
            self.current_semester
        )

    # SWITCH SEMESTER
    def switch_semester(self, event=None):

        selected = self.semester_var.get()

        if selected not in self.semesters:
            return

        self.cancel_edit()

        self.current_semester = selected
        self.load_current_semester()
        self.refresh_table()

    # ADD SEMESTER
    def add_semester(self):

        name = simpledialog.askstring(
            "Add Semester",
            "Enter a semester name (e.g. Semester 2):",
            parent=self.root
        )

        if name is None:
            return

        name = name.strip()

        if not name:
            messagebox.showerror(
                "Invalid Name",
                "Semester name cannot be empty."
            )
            return

        try:
            self.db.add_semester(name)

        except sqlite3.IntegrityError:
            messagebox.showwarning(
                "Already Exists",
                "A semester with that name already exists."
            )
            return

        self.semesters = self.db.get_semesters()
        self.current_semester = name

        self.cancel_edit()
        self.load_current_semester()
        self.update_semester_dropdown()
        self.refresh_table()

    # DELETE SEMESTER
    def delete_semester(self):

        if len(self.semesters) == 1:
            messagebox.showwarning(
                "Cannot Delete",
                "At least one semester must remain."
            )
            return

        confirm = messagebox.askyesno(
            "Delete Semester",
            f"Delete {self.current_semester} and all its subjects?"
        )

        if not confirm:
            return

        self.db.delete_semester(self.current_semester)

        self.semesters = self.db.get_semesters()
        self.current_semester = self.semesters[0]

        self.cancel_edit()
        self.load_current_semester()
        self.update_semester_dropdown()
        self.refresh_table()

    # DATABASE STATUS BUTTON
    def save_semester(self):

        messagebox.showinfo(
            "Database Status",
            "Your changes are automatically saved to cgpa_studio.db.\n\n"
            "No manual saving is required."
        )

    # GET AND VALIDATE INPUT
    def get_input(self):

        name = self.subject_entry.get().strip()

        try:
            credits = float(self.credit_entry.get())
            grade = float(self.grade_entry.get())

            if not name:
                raise ValueError("Enter a subject name.")

            if credits <= 0:
                raise ValueError("Credits must be positive.")

            if not 0 <= grade <= 10:
                raise ValueError(
                    "Grade point must be between 0 and 10."
                )

            return name, credits, grade

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))
            return None

    # ADD SUBJECT
    def add_subject(self):

        data = self.get_input()

        if data is None:
            return

        name, credits, grade = data

        try:
            self.db.add_subject(
                self.current_semester,
                name,
                credits,
                grade
            )

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not save subject:\n{error}"
            )
            return

        self.load_current_semester()
        self.refresh_table()
        self.clear_inputs()

    # EDIT SUBJECT
    def edit_subject(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Select a subject to edit."
            )
            return

        self.editing_id = selected[0]
        subject = self.subjects[self.editing_id]

        self.subject_entry.delete(0, tk.END)
        self.subject_entry.insert(0, subject["name"])

        self.credit_entry.delete(0, tk.END)
        self.credit_entry.insert(0, subject["credits"])

        self.grade_entry.delete(0, tk.END)
        self.grade_entry.insert(0, subject["grade"])

        self.action_button.config(
            text="Save Changes",
            command=self.save_edit
        )

        self.cancel_button.grid()

    # SAVE EDIT
    def save_edit(self):

        data = self.get_input()

        if data is None:
            return

        name, credits, grade = data

        try:
            self.db.update_subject(
                self.editing_id,
                name,
                credits,
                grade
            )

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not update subject:\n{error}"
            )
            return

        self.cancel_edit()
        self.load_current_semester()
        self.refresh_table()

    # CANCEL EDIT
    def cancel_edit(self):

        self.editing_id = None

        self.action_button.config(
            text="Add Subject",
            command=self.add_subject
        )

        self.cancel_button.grid_remove()
        self.clear_inputs()

    # DELETE SUBJECT
    def delete_subject(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Select a subject to delete."
            )
            return

        subject_id = selected[0]

        confirm = messagebox.askyesno(
            "Delete Subject",
            "Are you sure you want to delete this subject?"
        )

        if not confirm:
            return

        try:
            self.db.delete_subject(subject_id)

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not delete subject:\n{error}"
            )
            return

        self.cancel_edit()
        self.load_current_semester()
        self.refresh_table()

    # CLEAR CURRENT SEMESTER
    def clear_semester(self):

        if not self.subjects:
            return

        confirm = messagebox.askyesno(
            "Confirm",
            f"Delete all subjects from {self.current_semester}?"
        )

        if confirm:
            self.db.clear_semester(self.current_semester)

            self.cancel_edit()
            self.load_current_semester()
            self.refresh_table()

    # CLEAR INPUT FIELDS
    def clear_inputs(self):

        self.subject_entry.delete(0, tk.END)
        self.credit_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)

    # REFRESH TABLE
    def refresh_table(self):

        for item in self.table.get_children():
            self.table.delete(item)

        for subject_id, subject in self.subjects.items():

            self.table.insert(
                "",
                "end",
                iid=subject_id,
                values=(
                    subject["name"],
                    subject["credits"],
                    subject["grade"],
                    round(subject["points"], 2)
                )
            )

        self.calculate_sgpa()
        self.update_cgpa()

    # CALCULATE SGPA
    def calculate_sgpa(self):

        total_credits = sum(
            subject["credits"]
            for subject in self.subjects.values()
        )

        total_points = sum(
            subject["points"]
            for subject in self.subjects.values()
        )

        if total_credits == 0:
            self.sgpa_label.config(text="--")
            return None

        sgpa = total_points / total_credits
        self.sgpa_label.config(text=f"{sgpa:.2f}")

        return sgpa

    # CALCULATE CUMULATIVE CGPA
    def update_cgpa(self):

        all_subjects = self.db.get_all_subjects()

        total_credits = sum(
            subject["credits"]
            for subject in all_subjects
        )

        total_points = sum(
            subject["points"]
            for subject in all_subjects
        )

        if total_credits == 0:
            self.cgpa_label.config(text="--")
            return None

        cgpa = total_points / total_credits
        self.cgpa_label.config(text=f"{cgpa:.2f}")

        return cgpa


# RUN APPLICATION
if __name__ == "__main__":

    root = tk.Tk()
    app = CGPAStudio(root)
    root.mainloop()
