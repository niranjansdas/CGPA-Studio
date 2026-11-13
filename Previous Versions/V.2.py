
import tkinter as tk
from tkinter import ttk, messagebox


class CGPAStudio:

    def __init__(self, root):
        self.root = root
        self.root.title("CGPA Studio")
        self.root.geometry("950x620")
        self.root.minsize(800, 500)
        self.root.configure(bg="#101827")

        self.subjects = {}
        self.next_id = 0
        self.editing_id = None

        self.create_interface()

    def create_interface(self):

        # HEADER
        header = tk.Frame(self.root, bg="#101827")
        header.pack(fill="x", pady=12)

        tk.Label(
            header,
            text="CGPA STUDIO",
            font=("Arial", 26, "bold"),
            fg="white",
            bg="#101827"
        ).pack()

        tk.Label(
            header,
            text="Academic Performance Manager",
            font=("Arial", 10),
            fg="#9CA3AF",
            bg="#101827"
        ).pack()

        # SGPA DISPLAY CARD
        result_frame = tk.Frame(
            self.root,
            bg="#1E3A5F",
            padx=20,
            pady=12
        )
        result_frame.pack(fill="x", padx=30, pady=10)

        tk.Label(
            result_frame,
            text="CURRENT SGPA",
            font=("Arial", 11, "bold"),
            fg="#BFDBFE",
            bg="#1E3A5F"
        ).pack()

        self.result_label = tk.Label(
            result_frame,
            text="--",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="#1E3A5F"
        )
        self.result_label.pack()

        # INPUT SECTION
        input_frame = tk.Frame(
            self.root,
            bg="#1F2937",
            padx=12,
            pady=12
        )
        input_frame.pack(fill="x", padx=30, pady=10)

        labels = ["Subject", "Credits", "Grade Point"]

        for column, label in enumerate(labels):
            tk.Label(
                input_frame,
                text=label,
                fg="white",
                bg="#1F2937"
            ).grid(row=0, column=column, padx=8)

        self.subject_entry = tk.Entry(input_frame, width=22)
        self.credit_entry = tk.Entry(input_frame, width=10)
        self.grade_entry = tk.Entry(input_frame, width=10)

        self.subject_entry.grid(row=1, column=0, padx=8, pady=8)
        self.credit_entry.grid(row=1, column=1, padx=8, pady=8)
        self.grade_entry.grid(row=1, column=2, padx=8, pady=8)

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

        # TABLE
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

        self.table = ttk.Treeview(
            self.root,
            columns=("subject", "credits", "grade", "points"),
            show="headings",
            height=7
        )

        self.table.heading("subject", text="Subject")
        self.table.heading("credits", text="Credits")
        self.table.heading("grade", text="Grade Point")
        self.table.heading("points", text="Weighted Points")

        self.table.column("subject", width=300)
        self.table.column("credits", width=120)
        self.table.column("grade", width=140)
        self.table.column("points", width=160)

        self.table.pack(fill="both", expand=True, padx=30, pady=5)

        # MANAGEMENT BUTTONS
        button_frame = tk.Frame(
            self.root,
            bg="#101827"
        )
        button_frame.pack(pady=12)

        tk.Button(
            button_frame,
            text="Edit Selected",
            command=self.edit_subject,
            bg="#D97706",
            fg="white",
            padx=12
        ).pack(side="left", padx=6)

        tk.Button(
            button_frame,
            text="Delete Selected",
            command=self.delete_subject,
            bg="#DC2626",
            fg="white",
            padx=12
        ).pack(side="left", padx=6)

        tk.Button(
            button_frame,
            text="Clear Semester",
            command=self.clear_semester,
            bg="#6B7280",
            fg="white",
            padx=12
        ).pack(side="left", padx=6)

        tk.Button(
            button_frame,
            text="Calculate SGPA",
            command=self.calculate_sgpa,
            bg="#059669",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        ).pack(side="left", padx=6)

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
                raise ValueError("Grade point must be between 0 and 10.")

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

        subject_id = str(self.next_id)
        self.next_id += 1

        self.subjects[subject_id] = {
            "name": name,
            "credits": credits,
            "grade": grade,
            "points": credits * grade
        }

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

        self.subjects[self.editing_id] = {
            "name": name,
            "credits": credits,
            "grade": grade,
            "points": credits * grade
        }

        self.cancel_edit()
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

        del self.subjects[subject_id]

        self.cancel_edit()
        self.refresh_table()

    # CLEAR SEMESTER
    def clear_semester(self):

        if not self.subjects:
            return

        confirm = messagebox.askyesno(
            "Confirm",
            "Delete all subjects from this semester?"
        )

        if confirm:
            self.subjects.clear()
            self.cancel_edit()
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

    # CALCULATE SGPA
    def calculate_sgpa(self):

        if not self.subjects:
            self.result_label.config(text="--")
            return

        total_points = sum(
            subject["points"]
            for subject in self.subjects.values()
        )

        total_credits = sum(
            subject["credits"]
            for subject in self.subjects.values()
        )

        sgpa = total_points / total_credits

        self.result_label.config(
            text=f"{sgpa:.2f}"
        )


# RUN APPLICATION
if __name__ == "__main__":

    root = tk.Tk()
    app = CGPAStudio(root)
    root.mainloop()
