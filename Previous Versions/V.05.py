
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3


class CGPAStudio:

    def __init__(self, root):
        self.root = root
        self.root.title("CGPA Studio | Version 0.5")
        self.root.geometry("1150x800")
        self.root.minsize(950, 650)
        self.root.configure(bg="#101827")

        self.db = None

        try:
            from database import CGPADatabase
            self.db = CGPADatabase()
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not connect to database:\n{error}"
            )
            self.root.destroy()
            return

        self.semesters = self.db.get_semesters()
        self.current_semester = self.semesters[0]
        self.subjects = self.db.get_subjects(self.current_semester)
        self.editing_id = None

        self.create_interface()
        self.refresh_table()
        self.refresh_analytics()

    # -------------------------------------------------
    # MAIN INTERFACE
    # -------------------------------------------------

    def create_interface(self):

        header = tk.Frame(self.root, bg="#101827")
        header.pack(fill="x", pady=(12, 8))

        tk.Label(
            header,
            text="CGPA STUDIO",
            font=("Arial", 25, "bold"),
            fg="white",
            bg="#101827"
        ).pack()

        tk.Label(
            header,
            text="Academic Performance Manager | Version 0.5",
            font=("Arial", 10),
            fg="#9CA3AF",
            bg="#101827"
        ).pack()

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TNotebook",
            background="#101827",
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background="#374151",
            foreground="white",
            padding=(20, 10),
            font=("Arial", 10, "bold")
        )

        style.map(
            "TNotebook.Tab",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "white")]
        )

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(
            fill="both", expand=True, padx=20, pady=10
        )

        self.calculator_tab = tk.Frame(
            self.notebook, bg="#101827"
        )

        self.analytics_tab = tk.Frame(
            self.notebook, bg="#101827"
        )

        self.notebook.add(
            self.calculator_tab, text="  Calculator  "
        )

        self.notebook.add(
            self.analytics_tab, text="  Analytics Dashboard  "
        )

        self.create_calculator()
        self.create_analytics()

    # -------------------------------------------------
    # CALCULATOR TAB
    # -------------------------------------------------

    def create_calculator(self):

        # RESULT CARDS

        cards = tk.Frame(self.calculator_tab, bg="#101827")
        cards.pack(fill="x", padx=10, pady=10)

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
            self.calculator_tab,
            bg="#1F2937",
            padx=12,
            pady=10
        )
        semester_frame.pack(fill="x", padx=10, pady=5)

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
            self.calculator_tab,
            bg="#1F2937",
            padx=12,
            pady=10
        )
        input_frame.pack(fill="x", padx=10, pady=8)

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

        self.subject_entry.grid(row=1, column=0, padx=8, pady=7)
        self.credit_entry.grid(row=1, column=1, padx=8, pady=7)
        self.grade_entry.grid(row=1, column=2, padx=8, pady=7)

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
            self.calculator_tab,
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
            fill="both", expand=True, padx=10, pady=5
        )

        # MANAGEMENT BUTTONS

        button_frame = tk.Frame(
            self.calculator_tab, bg="#101827"
        )
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
            self.calculator_tab,
            text="All changes are automatically saved.",
            font=("Arial", 9),
            fg="#86EFAC",
            bg="#101827"
        )
        self.status_label.pack(pady=5)

    # -------------------------------------------------
    # SEMESTER MANAGEMENT
    # -------------------------------------------------

    def update_semester_dropdown(self):
        self.semester_dropdown["values"] = self.semesters
        self.semester_var.set(self.current_semester)

    def load_current_semester(self):
        self.subjects = self.db.get_subjects(
            self.current_semester
        )

    def switch_semester(self, event=None):

        selected = self.semester_var.get()

        if selected not in self.semesters:
            return

        self.cancel_edit()
        self.current_semester = selected
        self.load_current_semester()
        self.refresh_table()

    def add_semester(self):

        name = simpledialog.askstring(
            "Add Semester",
            "Enter a semester name:",
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
                "This semester already exists."
            )
            return

        self.semesters = self.db.get_semesters()
        self.current_semester = name

        self.cancel_edit()
        self.load_current_semester()
        self.update_semester_dropdown()
        self.refresh_table()

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

    def save_semester(self):

        messagebox.showinfo(
            "Database Status",
            "All changes are automatically saved to cgpa_studio.db."
        )

    # -------------------------------------------------
    # SUBJECT MANAGEMENT
    # -------------------------------------------------

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
                "Database Error", str(error)
            )
            return

        self.load_current_semester()
        self.refresh_table()
        self.clear_inputs()

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
                "Database Error", str(error)
            )
            return

        self.cancel_edit()
        self.load_current_semester()
        self.refresh_table()

    def cancel_edit(self):

        self.editing_id = None

        self.action_button.config(
            text="Add Subject",
            command=self.add_subject
        )

        self.cancel_button.grid_remove()
        self.clear_inputs()

    def delete_subject(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Select a subject to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Delete Subject",
            "Are you sure you want to delete this subject?"
        )

        if not confirm:
            return

        self.db.delete_subject(selected[0])

        self.cancel_edit()
        self.load_current_semester()
        self.refresh_table()

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

    def clear_inputs(self):

        self.subject_entry.delete(0, tk.END)
        self.credit_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)

    # -------------------------------------------------
    # CALCULATIONS
    # -------------------------------------------------

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
        self.refresh_analytics()

    def calculate_sgpa(self):

        total_credits = sum(
            s["credits"] for s in self.subjects.values()
        )

        total_points = sum(
            s["points"] for s in self.subjects.values()
        )

        if total_credits == 0:
            self.sgpa_label.config(text="--")
            return None

        sgpa = total_points / total_credits
        self.sgpa_label.config(text=f"{sgpa:.2f}")

        return sgpa

    def update_cgpa(self):

        all_subjects = self.db.get_all_subjects()

        total_credits = sum(
            s["credits"] for s in all_subjects
        )

        total_points = sum(
            s["points"] for s in all_subjects
        )

        if total_credits == 0:
            self.cgpa_label.config(text="--")
            return None

        cgpa = total_points / total_credits
        self.cgpa_label.config(text=f"{cgpa:.2f}")

        return cgpa

    # -------------------------------------------------
    # ANALYTICS DASHBOARD
    # -------------------------------------------------

    def create_analytics(self):

        # SCROLLABLE DASHBOARD

        container = tk.Frame(
            self.analytics_tab, bg="#101827"
        )
        container.pack(fill="both", expand=True)

        self.analytics_canvas = tk.Canvas(
            container,
            bg="#101827",
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.analytics_canvas.yview
        )

        self.analytics_canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")
        self.analytics_canvas.pack(
            side="left", fill="both", expand=True
        )

        self.dashboard = tk.Frame(
            self.analytics_canvas, bg="#101827"
        )

        self.dashboard_window = self.analytics_canvas.create_window(
            (0, 0),
            window=self.dashboard,
            anchor="nw"
        )

        self.dashboard.bind(
            "<Configure>",
            lambda event: self.analytics_canvas.configure(
                scrollregion=self.analytics_canvas.bbox("all")
            )
        )

        self.analytics_canvas.bind(
            "<Configure>",
            lambda event: self.analytics_canvas.itemconfigure(
                self.dashboard_window,
                width=event.width
            )
        )

        self.analytics_canvas.bind_all(
            "<MouseWheel>",
            self.on_analytics_scroll
        )

        # DASHBOARD TITLE

        tk.Label(
            self.dashboard,
            text="ACADEMIC ANALYTICS",
            font=("Arial", 19, "bold"),
            fg="white",
            bg="#101827"
        ).pack(anchor="w", padx=15, pady=(12, 2))

        tk.Label(
            self.dashboard,
            text="Track your academic progress across semesters.",
            font=("Arial", 10),
            fg="#9CA3AF",
            bg="#101827"
        ).pack(anchor="w", padx=15, pady=(0, 12))

        # SUMMARY CARDS

        self.summary_frame = tk.Frame(
            self.dashboard, bg="#101827"
        )
        self.summary_frame.pack(fill="x", padx=10, pady=5)

        self.summary_labels = {}

        summary_items = [
            ("cgpa", "OVERALL CGPA", "#1E3A5F", "#BFDBFE"),
            ("semesters", "SEMESTERS", "#374151", "#E5E7EB"),
            ("credits", "TOTAL CREDITS", "#174B3A", "#BBF7D0"),
            ("subjects", "TOTAL SUBJECTS", "#49351C", "#FDE68A")
        ]

        for key, title, bg, fg in summary_items:

            card = tk.Frame(
                self.summary_frame,
                bg=bg,
                padx=10,
                pady=12
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=4
            )

            tk.Label(
                card,
                text=title,
                font=("Arial", 9, "bold"),
                fg=fg,
                bg=bg
            ).pack()

            value_label = tk.Label(
                card,
                text="--",
                font=("Arial", 21, "bold"),
                fg="white",
                bg=bg
            )

            value_label.pack()
            self.summary_labels[key] = value_label

        # SEMESTER COMPARISON TABLE

        self.create_section_title(
            self.dashboard, "SEMESTER COMPARISON"
        )

        comparison_frame = tk.Frame(
            self.dashboard, bg="#1F2937"
        )
        comparison_frame.pack(
            fill="x", padx=15, pady=5
        )

        self.comparison_table = ttk.Treeview(
            comparison_frame,
            columns=("semester", "sgpa", "credits",
                     "subjects", "points", "change"),
            show="headings",
            height=6
        )

        headings = {
            "semester": "Semester",
            "sgpa": "SGPA",
            "credits": "Credits",
            "subjects": "Subjects",
            "points": "Weighted Points",
            "change": "SGPA Change"
        }

        widths = {
            "semester": 140,
            "sgpa": 90,
            "credits": 90,
            "subjects": 90,
            "points": 140,
            "change": 120
        }

        for column, heading in headings.items():
            self.comparison_table.heading(
                column, text=heading
            )
            self.comparison_table.column(
                column,
                width=widths[column],
                anchor="center"
            )

        self.comparison_table.pack(
            fill="x", padx=5, pady=5
        )

        # SGPA CHART

        self.create_section_title(
            self.dashboard, "SGPA COMPARISON"
        )

        self.sgpa_chart = tk.Canvas(
            self.dashboard,
            height=270,
            bg="#1F2937",
            highlightthickness=0
        )

        self.sgpa_chart.pack(
            fill="x", padx=15, pady=5
        )

        # CGPA CHART

        self.create_section_title(
            self.dashboard, "CUMULATIVE CGPA PROGRESSION"
        )

        self.cgpa_chart = tk.Canvas(
            self.dashboard,
            height=270,
            bg="#1F2937",
            highlightthickness=0
        )

        self.cgpa_chart.pack(
            fill="x", padx=15, pady=5
        )

        # GRADE DISTRIBUTION

        self.create_section_title(
            self.dashboard, "GRADE DISTRIBUTION"
        )

        self.grade_chart = tk.Canvas(
            self.dashboard,
            height=180,
            bg="#1F2937",
            highlightthickness=0
        )

        self.grade_chart.pack(
            fill="x", padx=15, pady=5
        )

        # PERFORMANCE INSIGHTS

        self.create_section_title(
            self.dashboard, "PERFORMANCE INSIGHTS"
        )

        self.insights_frame = tk.Frame(
            self.dashboard,
            bg="#1F2937",
            padx=15,
            pady=12
        )

        self.insights_frame.pack(
            fill="x", padx=15, pady=(5, 15)
        )

        self.insights_label = tk.Label(
            self.insights_frame,
            text="Add subjects to see your insights.",
            font=("Arial", 10),
            fg="white",
            bg="#1F2937",
            justify="left",
            anchor="w"
        )

        self.insights_label.pack(fill="x")

    # -------------------------------------------------
    # ANALYTICS HELPERS
    # -------------------------------------------------

    def on_analytics_scroll(self, event):

        if self.notebook.select() == str(self.analytics_tab):
            self.analytics_canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units"
            )

    def create_section_title(self, parent, title):

        tk.Label(
            parent,
            text=title,
            font=("Arial", 12, "bold"),
            fg="#93C5FD",
            bg="#101827"
        ).pack(anchor="w", padx=15, pady=(15, 5))

    def get_semester_statistics(self):

        statistics = []

        for semester in self.semesters:

            subjects = self.db.get_subjects(semester)

            credits = sum(
                s["credits"] for s in subjects.values()
            )

            points = sum(
                s["points"] for s in subjects.values()
            )

            sgpa = points / credits if credits else None

            statistics.append({
                "name": semester,
                "subjects": subjects,
                "credits": credits,
                "points": points,
                "count": len(subjects),
                "sgpa": sgpa
            })

        return statistics

    # -------------------------------------------------
    # REFRESH ANALYTICS
    # -------------------------------------------------

    def refresh_analytics(self):

        stats = self.get_semester_statistics()

        all_subjects = self.db.get_all_subjects()

        total_credits = sum(
            s["credits"] for s in all_subjects
        )

        total_points = sum(
            s["points"] for s in all_subjects
        )

        total_subjects = len(all_subjects)

        cgpa = (
            total_points / total_credits
            if total_credits else None
        )

        # SUMMARY CARDS

        self.summary_labels["cgpa"].config(
            text=f"{cgpa:.2f}" if cgpa is not None else "--"
        )

        self.summary_labels["semesters"].config(
            text=str(len(self.semesters))
        )

        self.summary_labels["credits"].config(
            text=f"{total_credits:g}"
        )

        self.summary_labels["subjects"].config(
            text=str(total_subjects)
        )

        # COMPARISON TABLE

        for item in self.comparison_table.get_children():
            self.comparison_table.delete(item)

        previous_sgpa = None

        for item in stats:

            sgpa = item["sgpa"]

            if sgpa is None:
                change = "--"
            elif previous_sgpa is None:
                change = "--"
            else:
                difference = sgpa - previous_sgpa
                change = f"{difference:+.2f}"

            self.comparison_table.insert(
                "",
                "end",
                values=(
                    item["name"],
                    f"{sgpa:.2f}" if sgpa is not None else "--",
                    f"{item['credits']:g}",
                    item["count"],
                    f"{item['points']:.2f}",
                    change
                )
            )

            if sgpa is not None:
                previous_sgpa = sgpa

        # CHARTS AND INSIGHTS

        self.draw_sgpa_chart(stats)
        self.draw_cgpa_chart(stats)
        self.draw_grade_chart(all_subjects)
        self.update_insights(stats, all_subjects, cgpa)

    # -------------------------------------------------
    # SGPA BAR CHART
    # -------------------------------------------------

    def draw_sgpa_chart(self, stats):

        canvas = self.sgpa_chart
        canvas.delete("all")

        canvas.update_idletasks()

        width = max(canvas.winfo_width(), 600)
        height = 270

        left = 55
        right = 25
        top = 25
        bottom = 55

        chart_height = height - top - bottom
        chart_width = width - left - right

        for value in range(0, 11, 2):

            y = top + chart_height * (10 - value) / 10

            canvas.create_line(
                left, y, width - right, y,
                fill="#374151"
            )

            canvas.create_text(
                left - 20, y,
                text=str(value),
                fill="#D1D5DB",
                font=("Arial", 9)
            )

        valid = [
            item for item in stats
            if item["sgpa"] is not None
        ]

        if not valid:
            canvas.create_text(
                width / 2, height / 2,
                text="Add subjects to view semester SGPA.",
                fill="white",
                font=("Arial", 11)
            )
            return

        slot = chart_width / len(valid)
        bar_width = min(45, slot * 0.55)

        for i, item in enumerate(valid):

            x_center = left + slot * (i + 0.5)

            bar_height = (
                item["sgpa"] / 10
            ) * chart_height

            x1 = x_center - bar_width / 2
            x2 = x_center + bar_width / 2
            y1 = top + chart_height - bar_height

            canvas.create_rectangle(
                x1, y1, x2, top + chart_height,
                fill="#3B82F6",
                outline=""
            )

            canvas.create_text(
                x_center, y1 - 12,
                text=f"{item['sgpa']:.2f}",
                fill="white",
                font=("Arial", 9, "bold")
            )

            canvas.create_text(
                x_center, top + chart_height + 18,
                text=item["name"],
                fill="#D1D5DB",
                font=("Arial", 8)
            )

    # -------------------------------------------------
    # CGPA PROGRESSION CHART
    # -------------------------------------------------

    def draw_cgpa_chart(self, stats):

        canvas = self.cgpa_chart
        canvas.delete("all")

        canvas.update_idletasks()

        width = max(canvas.winfo_width(), 600)
        height = 270

        left = 55
        right = 25
        top = 25
        bottom = 55

        chart_height = height - top - bottom
        chart_width = width - left - right

        for value in range(0, 11, 2):

            y = top + chart_height * (10 - value) / 10

            canvas.create_line(
                left, y, width - right, y,
                fill="#374151"
            )

            canvas.create_text(
                left - 20, y,
                text=str(value),
                fill="#D1D5DB",
                font=("Arial", 9)
            )

        cumulative_credits = 0
        cumulative_points = 0
        values = []

        for item in stats:

            cumulative_credits += item["credits"]
            cumulative_points += item["points"]

            if cumulative_credits > 0:
                values.append((
                    item["name"],
                    cumulative_points / cumulative_credits
                ))
            else:
                values.append((item["name"], None))

        valid = [
            (name, value)
            for name, value in values
            if value is not None
        ]

        if not valid:
            canvas.create_text(
                width / 2, height / 2,
                text="Add subjects to view CGPA progression.",
                fill="white",
                font=("Arial", 11)
            )
            return

        slot = chart_width / len(valid)
        coordinates = []

        for i, (name, value) in enumerate(valid):

            x = left + slot * (i + 0.5)
            y = top + chart_height * (10 - value) / 10

            coordinates.append((x, y))

            canvas.create_text(
                x, y - 17,
                text=f"{value:.2f}",
                fill="white",
                font=("Arial", 9, "bold")
            )

            canvas.create_text(
                x, top + chart_height + 18,
                text=name,
                fill="#D1D5DB",
                font=("Arial", 8)
            )

        for i in range(len(coordinates) - 1):

            x1, y1 = coordinates[i]
            x2, y2 = coordinates[i + 1]

            canvas.create_line(
                x1, y1, x2, y2,
                fill="#34D399",
                width=3
            )

        for x, y in coordinates:

            canvas.create_oval(
                x - 5, y - 5,
                x + 5, y + 5,
                fill="#34D399",
                outline=""
            )

    # -------------------------------------------------
    # GRADE DISTRIBUTION
    # -------------------------------------------------

    def draw_grade_chart(self, all_subjects):

        canvas = self.grade_chart
        canvas.delete("all")

        canvas.update_idletasks()

        width = max(canvas.winfo_width(), 600)

        ranges = [
            ("0–3.99", 0, 4),
            ("4–5.99", 4, 6),
            ("6–7.99", 6, 8),
            ("8–10", 8, 10.000001)
        ]

        counts = []

        for label, low, high in ranges:

            count = sum(
                1 for s in all_subjects
                if low <= s["grade"] < high
            )

            counts.append((label, count))

        maximum = max(
            (count for _, count in counts),
            default=0
        )

        if maximum == 0:
            canvas.create_text(
                width / 2, 90,
                text="Add subjects to view grade distribution.",
                fill="white",
                font=("Arial", 11)
            )
            return

        left = 100
        bar_width = width - 200

        for i, (label, count) in enumerate(counts):

            y = 25 + i * 38

            canvas.create_text(
                left - 15, y + 10,
                text=label,
                fill="#D1D5DB",
                anchor="e",
                font=("Arial", 9)
            )

            length = bar_width * count / maximum

            canvas.create_rectangle(
                left, y,
                left + length, y + 20,
                fill="#8B5CF6",
                outline=""
            )

            canvas.create_text(
                left + length + 12,
                y + 10,
                text=str(count),
                fill="white",
                anchor="w",
                font=("Arial", 9, "bold")
            )

    # -------------------------------------------------
    # PERFORMANCE INSIGHTS
    # -------------------------------------------------

    def update_insights(self, stats, all_subjects, cgpa):

        valid = [
            item for item in stats
            if item["sgpa"] is not None
        ]

        lines = []

        if not all_subjects:

            lines.append(
                "Add subjects to generate your academic insights."
            )

            self.insights_label.config(
                text="\n".join(lines)
            )
            return

        if valid:

            best = max(valid, key=lambda x: x["sgpa"])
            worst = min(valid, key=lambda x: x["sgpa"])

            average_sgpa = sum(
                item["sgpa"] for item in valid
            ) / len(valid)

            lines.append(
                f"Highest-performing semester: "
                f"{best['name']} ({best['sgpa']:.2f})"
            )

            lines.append(
                f"Lowest-performing semester: "
                f"{worst['name']} ({worst['sgpa']:.2f})"
            )

            lines.append(
                f"Average semester SGPA: {average_sgpa:.2f}"
            )

        best_subject = max(
            all_subjects,
            key=lambda x: x["grade"]
        )

        lines.append(
            f"Highest grade-point subject: "
            f"{best_subject['subject']} "
            f"({best_subject['grade']:g})"
        )

        lines.append(
            f"Total weighted grade points: {sum(s['points'] for s in all_subjects):.2f}"
        )

        lines.append(
            f"Overall CGPA: {cgpa:.2f}"
        )

        self.insights_label.config(
            text="\n\n".join(lines)
        )


# -------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()
    app = CGPAStudio(root)
    root.mainloop()
