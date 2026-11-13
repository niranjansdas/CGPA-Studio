
import tkinter as tk
from tkinter import ttk, messagebox


class CGPAStudio:

    def __init__(self, root):
        self.root = root
        self.root.title("CGPA Studio")
        self.root.geometry("850x600")
        self.root.configure(bg="#101827")

        self.subjects = []

        self.create_interface()

    def create_interface(self):

        title = tk.Label(
            self.root,
            text="CGPA STUDIO",
            font=("Arial", 26, "bold"),
            fg="white",
            bg="#101827"
        )
        title.pack(pady=20)

        subtitle = tk.Label(
            self.root,
            text="Your Academic Performance Calculator",
            font=("Arial", 11),
            fg="#9CA3AF",
            bg="#101827"
        )
        subtitle.pack()

        # Input section
        input_frame = tk.Frame(self.root, bg="#1F2937", padx=15, pady=15)
        input_frame.pack(pady=25, padx=30, fill="x")

        tk.Label(input_frame, text="Subject", fg="white",
                 bg="#1F2937").grid(row=0, column=0, padx=8)

        tk.Label(input_frame, text="Credits", fg="white",
                 bg="#1F2937").grid(row=0, column=1, padx=8)

        tk.Label(input_frame, text="Grade Point", fg="white",
                 bg="#1F2937").grid(row=0, column=2, padx=8)

        self.subject_entry = tk.Entry(input_frame, width=22)
        self.credit_entry = tk.Entry(input_frame, width=10)
        self.grade_entry = tk.Entry(input_frame, width=12)

        self.subject_entry.grid(row=1, column=0, padx=8, pady=10)
        self.credit_entry.grid(row=1, column=1, padx=8, pady=10)
        self.grade_entry.grid(row=1, column=2, padx=8, pady=10)

        add_button = tk.Button(
            input_frame,
            text="Add Subject",
            command=self.add_subject,
            bg="#2563EB",
            fg="white",
            padx=15
        )
        add_button.grid(row=1, column=3, padx=10)

        # Subject table
        self.table = ttk.Treeview(
            self.root,
            columns=("subject", "credits", "grade", "points"),
            show="headings",
            height=10
        )

        self.table.heading("subject", text="Subject")
        self.table.heading("credits", text="Credits")
        self.table.heading("grade", text="Grade Point")
        self.table.heading("points", text="Weighted Points")

        self.table.column("subject", width=250)
        self.table.column("credits", width=120)
        self.table.column("grade", width=150)
        self.table.column("points", width=150)

        self.table.pack(padx=30, fill="x")

        # Calculate button
        calculate_button = tk.Button(
            self.root,
            text="Calculate SGPA",
            command=self.calculate_sgpa,
            font=("Arial", 12, "bold"),
            bg="#059669",
            fg="white",
            padx=25,
            pady=10
        )
        calculate_button.pack(pady=20)

        self.result_label = tk.Label(
            self.root,
            text="Your SGPA will appear here",
            font=("Arial", 18, "bold"),
            fg="#60A5FA",
            bg="#101827"
        )
        self.result_label.pack(pady=10)

    def add_subject(self):

        name = self.subject_entry.get().strip()

        try:
            credits = float(self.credit_entry.get())
            grade = float(self.grade_entry.get())

            if not name:
                raise ValueError("Enter a subject name.")

            if credits <= 0 or grade < 0:
                raise ValueError("Credits must be positive and grade cannot be negative.")

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))
            return

        weighted_points = credits * grade

        self.subjects.append({
            "name": name,
            "credits": credits,
            "grade": grade,
            "points": weighted_points
        })

        self.table.insert(
            "",
            "end",
            values=(name, credits, grade, weighted_points)
        )

        self.subject_entry.delete(0, tk.END)
        self.credit_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)

    def calculate_sgpa(self):

        if not self.subjects:
            messagebox.showwarning("Warning", "Add subjects first.")
            return

        total_points = sum(subject["points"] for subject in self.subjects)
        total_credits = sum(subject["credits"] for subject in self.subjects)

        sgpa = total_points / total_credits

        self.result_label.config(
            text=f"Your SGPA: {sgpa:.2f}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = CGPAStudio(root)
    root.mainloop()
