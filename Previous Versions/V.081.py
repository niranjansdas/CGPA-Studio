
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3


class CGPAStudio:

    VERSION = "0.8"

    BG = "#0B1120"
    SIDEBAR = "#101A2D"
    PANEL = "#162238"
    CARD = "#1B2A43"
    BLUE = "#3B82F6"
    BLUE_HOVER = "#2563EB"
    TEXT = "#F1F5F9"
    MUTED = "#94A3B8"
    GREEN = "#34D399"
    RED = "#F87171"

    def __init__(self, root):

        self.root = root
        self.root.title(f"CGPA Studio | Version {self.VERSION}")
        self.root.geometry("1250x800")
        self.root.minsize(1050, 680)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root.configure(fg_color=self.BG)

        try:
            from database import CGPADatabase
            self.db = CGPADatabase()

        except Exception as error:
            messagebox.showerror("Database Error", str(error))
            self.root.destroy()
            return

        self.semesters = self.db.get_semesters()

        if not self.semesters:
            self.db.add_semester("Semester 1")
            self.semesters = self.db.get_semesters()

        self.current_semester = self.semesters[0]
        self.subjects = self.db.get_subjects(self.current_semester)

        self.editing_id = None
        self.active_page = "Overview"

        self.create_layout()
        self.show_page("Overview")

    # =====================================================
    # MAIN LAYOUT
    # =====================================================

    def create_layout(self):

        self.sidebar = ctk.CTkFrame(
            self.root,
            width=230,
            corner_radius=0,
            fg_color=self.SIDEBAR
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color=self.BG
        )
        self.content.pack(side="right", fill="both", expand=True)

        self.create_sidebar()

    # =====================================================
    # SIDEBAR
    # =====================================================

    def create_sidebar(self):

        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(fill="x", padx=20, pady=(30, 35))

        ctk.CTkLabel(
            logo, text="CGPA",
            font=("Segoe UI", 27, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo, text="STUDIO",
            font=("Segoe UI", 15, "bold"),
            text_color=self.BLUE
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="WORKSPACE",
            font=("Segoe UI", 10, "bold"),
            text_color=self.MUTED
        ).pack(anchor="w", padx=22, pady=(0, 12))

        self.nav_buttons = {}

        pages = [
            ("Overview", "⌂"),
            ("Calculator", "▦"),
            ("Analytics", "▥"),
            ("CGPA Predictor", "↗")
        ]

        for page, symbol in pages:

            button = ctk.CTkButton(
                self.sidebar,
                text=f"   {symbol}    {page}",
                anchor="w",
                height=43,
                corner_radius=9,
                font=("Segoe UI", 13),
                fg_color="transparent",
                hover_color="#203452",
                text_color=self.TEXT,
                command=lambda p=page: self.show_page(p)
            )

            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[page] = button

        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.sidebar,
            text="DATA MANAGEMENT",
            font=("Segoe UI", 10, "bold"),
            text_color=self.MUTED
        ).pack(anchor="w", padx=22, pady=(10, 8))

        ctk.CTkButton(
            self.sidebar,
            text="   Backup Database",
            anchor="w",
            fg_color="transparent",
            hover_color="#203452",
            command=self.backup_database
        ).pack(fill="x", padx=12, pady=3)

        ctk.CTkButton(
            self.sidebar,
            text="   Restore Database",
            anchor="w",
            fg_color="transparent",
            hover_color="#203452",
            command=self.restore_database
        ).pack(fill="x", padx=12, pady=3)

        ctk.CTkButton(
            self.sidebar,
            text="   Database Location",
            anchor="w",
            fg_color="transparent",
            hover_color="#203452",
            command=self.show_database_location
        ).pack(fill="x", padx=12, pady=3)

        bottom = ctk.CTkFrame(
            self.sidebar,
            fg_color="#1A2940",
            corner_radius=12
        )
        bottom.pack(fill="x", padx=12, pady=18)

        ctk.CTkLabel(
            bottom,
            text="DAS & CO.",
            font=("Georgia", 15, "bold"),
            text_color="#FBBF24"
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            bottom,
            text=f"CGPA Studio v{self.VERSION}",
            font=("Segoe UI", 10),
            text_color=self.MUTED
        ).pack(anchor="w", padx=12, pady=(0, 10))

        ctk.CTkButton(
            bottom,
            text="About",
            height=28,
            fg_color="transparent",
            hover_color="#263B59",
            command=self.show_about
        ).pack(fill="x", padx=8, pady=(0, 8))

    # =====================================================
    # NAVIGATION
    # =====================================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, page):

        self.active_page = page
        self.editing_id = None
        self.clear_content()

        for name, button in self.nav_buttons.items():
            button.configure(
                fg_color="#1D3A63" if name == page else "transparent",
                text_color=self.TEXT
            )

        if page == "Overview":
            self.create_overview()

        elif page == "Calculator":
            self.create_calculator()

        elif page == "Analytics":
            self.create_analytics()

        elif page == "CGPA Predictor":
            self.create_predictor()

    # =====================================================
    # HEADER
    # =====================================================

    def create_header(self, title, subtitle):

        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", padx=35, pady=(30, 22))

        ctk.CTkLabel(
            header,
            text=title,
            font=("Segoe UI", 27, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=subtitle,
            font=("Segoe UI", 12),
            text_color=self.MUTED
        ).pack(anchor="w", pady=(5, 0))

    # =====================================================
    # DATA HELPERS
    # =====================================================

    def refresh_data(self):

        self.semesters = self.db.get_semesters()

        if not self.semesters:
            self.db.add_semester("Semester 1")
            self.semesters = self.db.get_semesters()

        if self.current_semester not in self.semesters:
            self.current_semester = self.semesters[0]

        self.subjects = self.db.get_subjects(self.current_semester)

    def get_academic_data(self):

        semesters = self.db.get_semesters()
        all_subjects = self.db.get_all_subjects()

        total_credits = sum(s["credits"] for s in all_subjects)
        total_points = sum(s["points"] for s in all_subjects)

        cgpa = total_points / total_credits if total_credits else 0

        semester_data = []

        for semester in semesters:

            subjects = self.db.get_subjects(semester)

            credits = sum(s["credits"] for s in subjects.values())
            points = sum(s["points"] for s in subjects.values())

            sgpa = points / credits if credits else 0

            semester_data.append({
                "name": semester,
                "credits": credits,
                "points": points,
                "sgpa": sgpa,
                "subjects": len(subjects)
            })

        return {
            "semesters": semester_data,
            "subjects": all_subjects,
            "total_credits": total_credits,
            "total_points": total_points,
            "cgpa": cgpa,
            "total_subjects": len(all_subjects)
        }

    # =====================================================
    # OVERVIEW
    # =====================================================

    def create_overview(self):

        self.refresh_data()
        data = self.get_academic_data()

        self.create_header(
            "Overview",
            "Your academic performance at a glance."
        )

        cards_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        cards_frame.pack(fill="x", padx=28)

        metrics = [
            ("OVERALL CGPA", f"{data['cgpa']:.2f}", self.BLUE),
            ("TOTAL CREDITS", f"{data['total_credits']:g}", self.GREEN),
            ("SEMESTERS", str(len(data["semesters"])), "#A78BFA"),
            ("SUBJECTS", str(data["total_subjects"]), "#FBBF24")
        ]

        for title, value, accent in metrics:

            card = ctk.CTkFrame(
                cards_frame, fg_color=self.PANEL, corner_radius=14
            )
            card.pack(side="left", fill="both", expand=True, padx=7)

            ctk.CTkLabel(
                card, text=title,
                font=("Segoe UI", 10, "bold"),
                text_color=self.MUTED
            ).pack(anchor="w", padx=17, pady=(18, 5))

            ctk.CTkLabel(
                card, text=value,
                font=("Segoe UI", 28, "bold"),
                text_color=accent
            ).pack(anchor="w", padx=17, pady=(0, 18))

        welcome = ctk.CTkFrame(
            self.content, fg_color=self.PANEL, corner_radius=15
        )
        welcome.pack(fill="x", padx=35, pady=25)

        ctk.CTkLabel(
            welcome,
            text="Your academic journey, organised.",
            font=("Segoe UI", 19, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=22, pady=(20, 5))

        ctk.CTkLabel(
            welcome,
            text="Manage your semesters, track your grades and understand your academic progress from one place.",
            font=("Segoe UI", 12),
            text_color=self.MUTED
        ).pack(anchor="w", padx=22, pady=(0, 18))

        ctk.CTkButton(
            welcome,
            text="Open Calculator  →",
            width=170,
            height=38,
            command=lambda: self.show_page("Calculator")
        ).pack(anchor="w", padx=22, pady=(0, 20))

        section = ctk.CTkFrame(
            self.content, fg_color=self.PANEL, corner_radius=15
        )
        section.pack(fill="both", expand=True, padx=35, pady=(0, 25))

        ctk.CTkLabel(
            section,
            text="SEMESTER PERFORMANCE",
            font=("Segoe UI", 13, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=20, pady=(18, 12))

        for semester in data["semesters"]:

            row = ctk.CTkFrame(
                section, fg_color="#1D2C45", corner_radius=9
            )
            row.pack(fill="x", padx=15, pady=4)

            ctk.CTkLabel(
                row, text=semester["name"], width=170,
                anchor="w", font=("Segoe UI", 12, "bold"),
                text_color=self.TEXT
            ).pack(side="left", padx=15, pady=12)

            ctk.CTkLabel(
                row, text=f"{semester['credits']:g} credits",
                text_color=self.MUTED
            ).pack(side="left", padx=10)

            ctk.CTkLabel(
                row,
                text=f"SGPA: {semester['sgpa']:.2f}" if semester["credits"] else "No subjects yet",
                font=("Segoe UI", 12, "bold"),
                text_color=self.GREEN if semester["credits"] else self.MUTED
            ).pack(side="right", padx=18)

    # =====================================================
    # CALCULATOR
    # =====================================================

    def create_calculator(self):

        self.refresh_data()

        self.create_header(
            "Calculator",
            "Manage your subjects and calculate your semester SGPA."
        )

        controls = ctk.CTkFrame(
            self.content, fg_color=self.PANEL, corner_radius=12
        )
        controls.pack(fill="x", padx=30, pady=(0, 15))

        self.semester_var = tk.StringVar(value=self.current_semester)

        self.semester_dropdown = ctk.CTkComboBox(
            controls,
            values=self.semesters,
            variable=self.semester_var,
            width=190,
            command=self.switch_semester
        )
        self.semester_dropdown.pack(side="left", padx=15, pady=15)

        ctk.CTkButton(
            controls, text="+ Add Semester",
            width=130, command=self.add_semester
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            controls, text="Delete Semester",
            width=130, fg_color="#991B1B",
            hover_color="#B91C1C", command=self.delete_semester
        ).pack(side="left", padx=5)

        summary = ctk.CTkFrame(self.content, fg_color="transparent")
        summary.pack(fill="x", padx=25, pady=5)

        self.sgpa_label = self.create_metric_card(
            summary, "SEMESTER SGPA", "--", self.BLUE
        )
        self.cgpa_label = self.create_metric_card(
            summary, "OVERALL CGPA", "--", self.GREEN
        )

        form = ctk.CTkFrame(
            self.content, fg_color=self.PANEL, corner_radius=12
        )
        form.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(
            form, text="SUBJECT DETAILS",
            font=("Segoe UI", 12, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=17, pady=(14, 8))

        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.pack(fill="x", padx=12, pady=(0, 10))

        self.subject_entry = ctk.CTkEntry(
            fields, placeholder_text="Subject name", width=260, height=38
        )
        self.subject_entry.pack(side="left", padx=5)

        self.credit_entry = ctk.CTkEntry(
            fields, placeholder_text="Credits", width=115, height=38
        )
        self.credit_entry.pack(side="left", padx=5)

        self.grade_entry = ctk.CTkEntry(
            fields, placeholder_text="Grade point", width=125, height=38
        )
        self.grade_entry.pack(side="left", padx=5)

        self.action_button = ctk.CTkButton(
            fields, text="Add Subject",
            width=125, height=38, command=self.add_subject
        )
        self.action_button.pack(side="left", padx=8)

        self.cancel_button = ctk.CTkButton(
            fields, text="Cancel", width=85, height=38,
            fg_color="#475569", command=self.cancel_edit
        )

        table_frame = ctk.CTkFrame(
            self.content, fg_color=self.PANEL, corner_radius=12
        )
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        ctk.CTkLabel(
            table_frame, text="SUBJECT RECORDS",
            font=("Segoe UI", 12, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=15, pady=12)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#1B2A43",
            foreground="#F1F5F9",
            fieldbackground="#1B2A43",
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#263B59",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")]
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=("subject", "credits", "grade", "points"),
            show="headings",
            height=8
        )

        for column, heading in [
            ("subject", "Subject"),
            ("credits", "Credits"),
            ("grade", "Grade Point"),
            ("points", "Weighted Points")
        ]:
            self.table.heading(column, text=heading)

        self.table.column("subject", width=350)
        self.table.column("credits", width=120, anchor="center")
        self.table.column("grade", width=130, anchor="center")
        self.table.column("points", width=150, anchor="center")

        self.table.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        actions = ctk.CTkFrame(table_frame, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(0, 12))

        ctk.CTkButton(
            actions, text="Edit Selected", width=120,
            fg_color="#B45309", hover_color="#D97706",
            command=self.edit_subject
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions, text="Delete Selected", width=125,
            fg_color="#991B1B", hover_color="#B91C1C",
            command=self.delete_subject
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions, text="Clear Semester", width=125,
            fg_color="#475569", hover_color="#64748B",
            command=self.clear_semester
        ).pack(side="left", padx=4)

        self.status_label = ctk.CTkLabel(
            actions,
            text="Changes are automatically saved.",
            text_color=self.GREEN,
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="right", padx=10)

        self.refresh_table()

    def create_metric_card(self, parent, title, value, accent):

        card = ctk.CTkFrame(
            parent, fg_color=self.PANEL, corner_radius=12
        )
        card.pack(side="left", fill="both", expand=True, padx=7)

        ctk.CTkLabel(
            card, text=title, text_color=self.MUTED,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=18, pady=(12, 3))

        label = ctk.CTkLabel(
            card, text=value, text_color=accent,
            font=("Segoe UI", 25, "bold")
        )
        label.pack(anchor="w", padx=18, pady=(0, 12))

        return label

    # =====================================================
    # SEMESTER MANAGEMENT
    # =====================================================

    def switch_semester(self, selected):

        if selected not in self.semesters:
            return

        self.cancel_edit()
        self.current_semester = selected
        self.subjects = self.db.get_subjects(selected)
        self.refresh_table()

    def add_semester(self):

        name = simpledialog.askstring(
            "Add Semester", "Enter a semester name:", parent=self.root
        )

        if name is None:
            return

        name = name.strip()

        if not name:
            messagebox.showerror("Invalid Name", "Semester name cannot be empty.")
            return

        try:
            self.db.add_semester(name)
        except sqlite3.IntegrityError:
            messagebox.showwarning("Already Exists", "This semester already exists.")
            return

        self.current_semester = name
        self.refresh_data()
        self.show_page("Calculator")

    def delete_semester(self):

        if len(self.semesters) <= 1:
            messagebox.showwarning("Cannot Delete", "At least one semester must remain.")
            return

        if not messagebox.askyesno(
            "Delete Semester",
            f"Delete {self.current_semester} and all its subjects?"
        ):
            return

        self.db.delete_semester(self.current_semester)
        self.current_semester = self.db.get_semesters()[0]
        self.refresh_data()
        self.show_page("Calculator")

    # =====================================================
    # SUBJECT MANAGEMENT
    # =====================================================

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

    def add_subject(self):

        data = self.get_input()
        if data is None:
            return

        try:
            self.db.add_subject(self.current_semester, *data)
        except Exception as error:
            messagebox.showerror("Database Error", str(error))
            return

        self.refresh_table()
        self.clear_inputs()

    def edit_subject(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("Selection Required", "Select a subject to edit.")
            return

        self.editing_id = selected[0]
        subject = self.subjects[self.editing_id]

        self.subject_entry.delete(0, "end")
        self.subject_entry.insert(0, subject["name"])

        self.credit_entry.delete(0, "end")
        self.credit_entry.insert(0, str(subject["credits"]))

        self.grade_entry.delete(0, "end")
        self.grade_entry.insert(0, str(subject["grade"]))

        self.action_button.configure(
            text="Save Changes", command=self.save_edit
        )

        self.cancel_button.pack(side="left", padx=5)

    def save_edit(self):

        data = self.get_input()
        if data is None:
            return

        try:
            self.db.update_subject(self.editing_id, *data)
        except Exception as error:
            messagebox.showerror("Database Error", str(error))
            return

        self.cancel_edit()
        self.refresh_table()

    def cancel_edit(self):

        self.editing_id = None

        if hasattr(self, "action_button") and self.action_button.winfo_exists():
            self.action_button.configure(
                text="Add Subject", command=self.add_subject
            )

        if hasattr(self, "cancel_button") and self.cancel_button.winfo_exists():
            self.cancel_button.pack_forget()

        self.clear_inputs()

    def delete_subject(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("Selection Required", "Select a subject to delete.")
            return

        if not messagebox.askyesno("Delete Subject", "Are you sure you want to delete this subject?"):
            return

        self.db.delete_subject(selected[0])
        self.cancel_edit()
        self.refresh_table()

    def clear_semester(self):

        if not self.subjects:
            return

        if messagebox.askyesno(
            "Clear Semester",
            f"Delete all subjects from {self.current_semester}?"
        ):
            self.db.clear_semester(self.current_semester)
            self.cancel_edit()
            self.refresh_table()

    def clear_inputs(self):

        for entry in (
            self.subject_entry,
            self.credit_entry,
            self.grade_entry
        ):
            entry.delete(0, "end")

    # =====================================================
    # CALCULATIONS AND TABLE REFRESH
    # =====================================================

    def refresh_table(self):

        self.subjects = self.db.get_subjects(self.current_semester)

        for item in self.table.get_children():
            self.table.delete(item)

        for subject_id, subject in self.subjects.items():

            self.table.insert(
                "", "end", iid=subject_id,
                values=(
                    subject["name"],
                    subject["credits"],
                    subject["grade"],
                    f"{subject['points']:.2f}"
                )
            )

        credits = sum(s["credits"] for s in self.subjects.values())
        points = sum(s["points"] for s in self.subjects.values())

        sgpa = points / credits if credits else None

        all_subjects = self.db.get_all_subjects()
        total_credits = sum(s["credits"] for s in all_subjects)
        total_points = sum(s["points"] for s in all_subjects)

        cgpa = total_points / total_credits if total_credits else None

        self.sgpa_label.configure(
            text=f"{sgpa:.2f}" if sgpa is not None else "--"
        )
        self.cgpa_label.configure(
            text=f"{cgpa:.2f}" if cgpa is not None else "--"
        )

    # =====================================================
    # ANALYTICS PAGE
    # =====================================================

    def create_analytics(self):

        data = self.get_academic_data()

        self.create_header(
            "Academic Analytics",
            "Understand your academic performance through data."
        )

        scroll = ctk.CTkScrollableFrame(
            self.content, fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        cards = ctk.CTkFrame(scroll, fg_color="transparent")
        cards.pack(fill="x", pady=5)

        metrics = [
            ("OVERALL CGPA", f"{data['cgpa']:.2f}", self.BLUE),
            ("TOTAL CREDITS", f"{data['total_credits']:g}", self.GREEN),
            ("SEMESTERS", str(len(data["semesters"])), "#A78BFA"),
            ("SUBJECTS", str(data["total_subjects"]), "#FBBF24")
        ]

        for title, value, accent in metrics:

            card = ctk.CTkFrame(
                cards, fg_color=self.PANEL, corner_radius=12
            )
            card.pack(side="left", fill="both", expand=True, padx=5)

            ctk.CTkLabel(
                card, text=title,
                font=("Segoe UI", 10, "bold"),
                text_color=self.MUTED
            ).pack(anchor="w", padx=15, pady=(15, 5))

            ctk.CTkLabel(
                card, text=value,
                font=("Segoe UI", 25, "bold"),
                text_color=accent
            ).pack(anchor="w", padx=15, pady=(0, 15))

        table_panel = ctk.CTkFrame(
            scroll, fg_color=self.PANEL, corner_radius=12
        )
        table_panel.pack(fill="x", pady=12)

        ctk.CTkLabel(
            table_panel, text="SEMESTER-WISE PERFORMANCE",
            font=("Segoe UI", 13, "bold"), text_color=self.TEXT
        ).pack(anchor="w", padx=18, pady=15)

        table = ttk.Treeview(
            table_panel,
            columns=("semester", "sgpa", "credits", "subjects", "points"),
            show="headings",
            height=min(max(len(data["semesters"]), 2), 8)
        )

        headings = {
            "semester": "Semester",
            "sgpa": "SGPA",
            "credits": "Credits",
            "subjects": "Subjects",
            "points": "Weighted Points"
        }

        widths = {
            "semester": 180, "sgpa": 100, "credits": 100,
            "subjects": 100, "points": 150
        }

        for column, heading in headings.items():
            table.heading(column, text=heading)
            table.column(column, width=widths[column], anchor="center")

        for item in data["semesters"]:
            table.insert(
                "", "end",
                values=(
                    item["name"],
                    f"{item['sgpa']:.2f}" if item["credits"] else "--",
                    f"{item['credits']:g}",
                    item["subjects"],
                    f"{item['points']:.2f}"
                )
            )

        table.pack(fill="x", padx=15, pady=(0, 15))

        chart_panel = ctk.CTkFrame(
            scroll, fg_color=self.PANEL, corner_radius=12
        )
        chart_panel.pack(fill="x", pady=10)

        ctk.CTkLabel(
            chart_panel, text="SGPA COMPARISON",
            font=("Segoe UI", 13, "bold"), text_color=self.TEXT
        ).pack(anchor="w", padx=18, pady=15)

        chart = tk.Canvas(
            chart_panel, height=260,
            bg=self.PANEL, highlightthickness=0
        )
        chart.pack(fill="x", padx=12, pady=(0, 15))

        chart.bind(
            "<Configure>",
            lambda event: self.draw_sgpa_chart(chart, data["semesters"])
        )
        chart.after(
            100,
            lambda: self.draw_sgpa_chart(chart, data["semesters"])
        )

        progression_panel = ctk.CTkFrame(
            scroll, fg_color=self.PANEL, corner_radius=12
        )
        progression_panel.pack(fill="x", pady=10)

        ctk.CTkLabel(
            progression_panel, text="CUMULATIVE CGPA PROGRESSION",
            font=("Segoe UI", 13, "bold"), text_color=self.TEXT
        ).pack(anchor="w", padx=18, pady=15)

        progression_canvas = tk.Canvas(
            progression_panel, height=260,
            bg=self.PANEL, highlightthickness=0
        )
        progression_canvas.pack(fill="x", padx=12, pady=(0, 15))

        progression_canvas.bind(
            "<Configure>",
            lambda event: self.draw_cgpa_progression(
                progression_canvas, data["semesters"]
            )
        )
        progression_canvas.after(
            100,
            lambda: self.draw_cgpa_progression(
                progression_canvas, data["semesters"]
            )
        )

        distribution_panel = ctk.CTkFrame(
            scroll, fg_color=self.PANEL, corner_radius=12
        )
        distribution_panel.pack(fill="x", pady=10)

        ctk.CTkLabel(
            distribution_panel, text="GRADE DISTRIBUTION",
            font=("Segoe UI", 13, "bold"), text_color=self.TEXT
        ).pack(anchor="w", padx=18, pady=15)

        ranges = [
            ("0.00 – 3.99", 0, 3.99, "#F87171"),
            ("4.00 – 5.99", 4, 5.99, "#FBBF24"),
            ("6.00 – 7.99", 6, 7.99, "#60A5FA"),
            ("8.00 – 10.00", 8, 10, "#34D399")
        ]

        total = len(data["subjects"])

        for label, lower, upper, colour in ranges:

            count = sum(
                1 for subject in data["subjects"]
                if lower <= subject["grade"] <= upper
            )

            percentage = count / total * 100 if total else 0

            row = ctk.CTkFrame(
                distribution_panel, fg_color="transparent"
            )
            row.pack(fill="x", padx=18, pady=6)

            ctk.CTkLabel(
                row, text=label, width=130,
                anchor="w", text_color=self.TEXT
            ).pack(side="left")

            bar = ctk.CTkProgressBar(
                row, height=10, progress_color=colour,
                fg_color="#263B59"
            )
            bar.pack(side="left", fill="x", expand=True, padx=12)
            bar.set(percentage / 100)

            ctk.CTkLabel(
                row, text=f"{count} ({percentage:.1f}%)",
                width=110, anchor="e", text_color=self.MUTED
            ).pack(side="right")

        ctk.CTkLabel(
            distribution_panel,
            text="Distribution is based on individual subject grade points.",
            font=("Segoe UI", 10), text_color=self.MUTED
        ).pack(anchor="w", padx=18, pady=(10, 15))

        insights_panel = ctk.CTkFrame(
            scroll, fg_color=self.PANEL, corner_radius=12
        )
        insights_panel.pack(fill="x", pady=10)

        ctk.CTkLabel(
            insights_panel, text="ACADEMIC INSIGHTS",
            font=("Segoe UI", 13, "bold"), text_color=self.TEXT
        ).pack(anchor="w", padx=18, pady=15)

        completed = [
            s for s in data["semesters"] if s["credits"] > 0
        ]

        if completed:

            highest = max(completed, key=lambda x: x["sgpa"])
            lowest = min(completed, key=lambda x: x["sgpa"])
            average = sum(s["sgpa"] for s in completed) / len(completed)

            best_subject = max(
                data["subjects"],
                key=lambda x: x["grade"],
                default=None
            )

            lines = [
                f"Highest SGPA: {highest['name']} — {highest['sgpa']:.2f}",
                f"Lowest SGPA: {lowest['name']} — {lowest['sgpa']:.2f}",
                f"Average semester SGPA: {average:.2f}",
                f"Overall CGPA: {data['cgpa']:.2f}",
                f"Total weighted points: {data['total_points']:.2f}"
            ]

            if best_subject:
                lines.append(
                    f"Highest-grade subject: {best_subject['subject']} "
                    f"({best_subject['grade']:.2f})"
                )

            for line in lines:
                ctk.CTkLabel(
                    insights_panel, text="•  " + line,
                    font=("Segoe UI", 12), text_color=self.TEXT
                ).pack(anchor="w", padx=20, pady=5)

        else:
            ctk.CTkLabel(
                insights_panel,
                text="Add subject records to generate academic insights.",
                text_color=self.MUTED
            ).pack(anchor="w", padx=20, pady=10)

        ctk.CTkFrame(
            insights_panel, fg_color="transparent", height=10
        ).pack()

    # =====================================================
    # ANALYTICS CHARTS
    # =====================================================

    def draw_sgpa_chart(self, canvas, semesters):

        canvas.delete("all")

        width = max(canvas.winfo_width(), 400)
        height = 260

        left, right = 55, width - 25
        top, bottom = 20, height - 45
        chart_height = bottom - top

        for value in range(0, 11, 2):

            y = bottom - (value / 10) * chart_height

            canvas.create_line(left, y, right, y, fill="#30415D")
            canvas.create_text(
                30, y, text=str(value),
                fill=self.MUTED, font=("Segoe UI", 9)
            )

        valid = [s for s in semesters if s["credits"] > 0]

        if not valid:
            canvas.create_text(
                width / 2, height / 2,
                text="No semester data available",
                fill=self.MUTED
            )
            return

        slot = (right - left) / len(valid)
        bar_width = min(45, slot * 0.55)

        for index, semester in enumerate(valid):

            value = semester["sgpa"]
            x = left + slot * index + slot / 2
            y = bottom - (value / 10) * chart_height

            canvas.create_rectangle(
                x - bar_width / 2, y,
                x + bar_width / 2, bottom,
                fill=self.BLUE, outline=""
            )

            canvas.create_text(
                x, y - 12, text=f"{value:.2f}",
                fill=self.TEXT, font=("Segoe UI", 9, "bold")
            )

            canvas.create_text(
                x, bottom + 20,
                text=semester["name"].replace("Semester ", "S"),
                fill=self.MUTED, font=("Segoe UI", 8)
            )

    def draw_cgpa_progression(self, canvas, semesters):

        canvas.delete("all")

        width = max(canvas.winfo_width(), 400)
        height = 260

        left, right = 55, width - 25
        top, bottom = 20, height - 45
        chart_height = bottom - top

        for value in range(0, 11, 2):

            y = bottom - (value / 10) * chart_height

            canvas.create_line(left, y, right, y, fill="#30415D")
            canvas.create_text(
                30, y, text=str(value),
                fill=self.MUTED, font=("Segoe UI", 9)
            )

        cumulative_points = 0
        cumulative_credits = 0
        values = []

        for semester in semesters:

            cumulative_points += semester["points"]
            cumulative_credits += semester["credits"]

            values.append(
                cumulative_points / cumulative_credits
                if cumulative_credits else None
            )

        valid_indices = [
            i for i, value in enumerate(values)
            if value is not None
        ]

        if not valid_indices:
            canvas.create_text(
                width / 2, height / 2,
                text="No academic records available",
                fill=self.MUTED
            )
            return

        if len(semesters) == 1:
            x_positions = [(left + right) / 2]
        else:
            slot = (right - left) / (len(semesters) - 1)
            x_positions = [left + i * slot for i in range(len(semesters))]

        points = []

        for index in valid_indices:

            x = x_positions[index]
            value = values[index]
            y = bottom - (value / 10) * chart_height

            points.extend([x, y])

            canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4,
                fill=self.GREEN, outline=""
            )

            canvas.create_text(
                x, y - 13, text=f"{value:.2f}",
                fill=self.TEXT, font=("Segoe UI", 9, "bold")
            )

            canvas.create_text(
                x, bottom + 20,
                text=semesters[index]["name"].replace("Semester ", "S"),
                fill=self.MUTED, font=("Segoe UI", 8)
            )

        if len(points) >= 4:
            canvas.create_line(
                *points, fill=self.GREEN, width=3, smooth=True
            )

    # =====================================================
    # CGPA PREDICTOR
    # =====================================================

    def create_predictor(self):

        self.create_header(
            "CGPA Predictor",
            "Explore your possible academic outcomes and plan your target."
        )

        scroll = ctk.CTkScrollableFrame(
            self.content, fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        data = self.get_academic_data()

        current_panel = ctk.CTkFrame(
            scroll, fg_color=self.PANEL, corner_radius=14
        )
        current_panel.pack(fill="x", pady=8)

        ctk.CTkLabel(
            current_panel, text="CURRENT ACADEMIC PERFORMANCE",
            font=("Segoe UI", 13, "bold"), text_color=self.TEXT
        ).pack(anchor="w", padx=20, pady=(18, 10))

        metrics = [
            ("Current CGPA", f"{data['cgpa']:.2f}"),
            ("Completed Credits", f"{data['total_credits']:g}"),
            ("Completed Subjects", str(data["total_subjects"]))
        ]

        row = ctk.CTkFrame(current_panel, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 18))

        for title, value in metrics:

            card = ctk.CTkFrame(
                row, fg_color=self.CARD, corner_radius=10
            )
            card.pack(side="left", fill="both", expand=True, padx=6)

            ctk.CTkLabel(
                card, text=title.upper(),
                font=("Segoe UI", 9, "bold"), text_color=self.MUTED
            ).pack(anchor="w", padx=13, pady=(12, 4))

            ctk.CTkLabel(
                card, text=value,
                font=("Segoe UI", 23, "bold"), text_color=self.BLUE
            ).pack(anchor="w", padx=13, pady=(0, 12))

        input_panel = ctk.CTkFrame(
            scroll, fg_color=self.PANEL, corner_radius=14
        )
        input_panel.pack(fill="x", pady=10)

        ctk.CTkLabel(
            input_panel, text="PREDICTION SETTINGS",
            font=("Segoe UI", 13, "bold"), text_color=self.TEXT
        ).pack(anchor="w", padx=20, pady=(18, 12))

        fields = ctk.CTkFrame(input_panel, fg_color="transparent")
        fields.pack(fill="x", padx=15, pady=(0, 15))

        remaining_frame = ctk.CTkFrame(fields, fg_color="transparent")
        remaining_frame.pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkLabel(
            remaining_frame, text="Remaining Credits",
            text_color=self.MUTED
        ).pack(anchor="w", pady=(0, 6))

        self.remaining_entry = ctk.CTkEntry(
            remaining_frame,
            placeholder_text="Enter remaining credits",
            height=40
        )
        self.remaining_entry.pack(fill="x")

        target_frame = ctk.CTkFrame(fields, fg_color="transparent")
        target_frame.pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkLabel(
            target_frame, text="Target Final CGPA",
            text_color=self.MUTED
        ).pack(anchor="w", pady=(0, 6))

        self.target_entry = ctk.CTkEntry(target_frame, height=40)
        self.target_entry.insert(0, "8.50")
        self.target_entry.pack(fill="x")

        ctk.CTkButton(
            input_panel,
            text="Calculate My Academic Outlook",
            height=42,
            command=self.calculate_prediction
        ).pack(fill="x", padx=23, pady=(0, 18))

        self.prediction_results = ctk.CTkFrame(
            scroll, fg_color=self.PANEL, corner_radius=14
        )
        self.prediction_results.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.prediction_results,
            text="YOUR PROJECTED OUTCOME",
            font=("Segoe UI", 13, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=20, pady=(18, 12))

        self.prediction_labels = {}

        for key, title, colour in [
            ("maximum", "Maximum Possible Final CGPA", self.GREEN),
            ("projected", "Projected Final CGPA", self.BLUE),
            ("required", "Required Average SGPA", "#A78BFA")
        ]:

            card = ctk.CTkFrame(
                self.prediction_results, fg_color=self.CARD, corner_radius=10
            )
            card.pack(fill="x", padx=15, pady=5)

            ctk.CTkLabel(
                card, text=title,
                font=("Segoe UI", 11), text_color=self.MUTED
            ).pack(side="left", padx=15, pady=15)

            label = ctk.CTkLabel(
                card, text="--",
                font=("Segoe UI", 22, "bold"), text_color=colour
            )
            label.pack(side="right", padx=18)

            self.prediction_labels[key] = label

        self.prediction_status = ctk.CTkLabel(
            self.prediction_results,
            text="Enter your remaining credits and target CGPA to begin.",
            font=("Segoe UI", 12),
            text_color=self.MUTED,
            wraplength=700
        )
        self.prediction_status.pack(anchor="w", padx=20, pady=(15, 20))

        ctk.CTkLabel(
            scroll,
            text="Predictions assume the remaining credits are completed with the average SGPA specified by each scenario. Actual results may vary.",
            font=("Segoe UI", 10),
            text_color=self.MUTED,
            wraplength=800
        ).pack(anchor="w", padx=5, pady=10)

    def calculate_prediction(self):

        data = self.get_academic_data()

        try:
            remaining = float(self.remaining_entry.get())
            target = float(self.target_entry.get())

            if remaining <= 0:
                raise ValueError("Remaining credits must be greater than zero.")

            if not 0 <= target <= 10:
                raise ValueError("Target CGPA must be between 0 and 10.")

        except ValueError as error:
            messagebox.showerror("Invalid Prediction Input", str(error))
            return

        completed_credits = data["total_credits"]
        completed_points = data["total_points"]
        final_credits = completed_credits + remaining

        maximum = (
            completed_points + 10 * remaining
        ) / final_credits

        projected = (
            completed_points + data["cgpa"] * remaining
        ) / final_credits

        required = (
            target * final_credits - completed_points
        ) / remaining

        self.prediction_labels["maximum"].configure(
            text=f"{maximum:.2f}"
        )
        self.prediction_labels["projected"].configure(
            text=f"{projected:.2f}"
        )

        if required <= 0:
            required_text = "Already achieved"
        elif required > 10:
            required_text = "Above 10.00"
        else:
            required_text = f"{required:.2f}"

        self.prediction_labels["required"].configure(
            text=required_text
        )

        if target <= data["cgpa"]:
            status = (
                "You have already reached this target. "
                "Keep maintaining your performance!"
            )
            colour = self.GREEN

        elif required > 10:
            status = (
                "This target is mathematically unreachable "
                "with the remaining credits, even with a 10.00 SGPA."
            )
            colour = self.RED

        elif projected >= target:
            status = (
                "Your target is achievable, and your current "
                "performance projection is already above it."
            )
            colour = self.GREEN

        else:
            status = (
                f"Your target is achievable. You need an average "
                f"SGPA of {required:.2f} across your remaining credits."
            )
            colour = "#FBBF24"

        self.prediction_status.configure(
            text=status, text_color=colour
        )

    # =====================================================
    # BACKUP AND RESTORE
    # =====================================================

    def backup_database(self):

        path = filedialog.asksaveasfilename(
            title="Backup CGPA Studio",
            defaultextension=".db",
            initialfile="cgpa_studio_backup.db",
            filetypes=[("SQLite Database", "*.db")]
        )

        if not path:
            return

        try:
            saved = self.db.create_backup(path)
            messagebox.showinfo(
                "Backup Successful", f"Backup saved to:\n{saved}"
            )
        except Exception as error:
            messagebox.showerror("Backup Failed", str(error))

    def restore_database(self):

        path = filedialog.askopenfilename(
            title="Select CGPA Studio Backup",
            filetypes=[("SQLite Database", "*.db")]
        )

        if not path:
            return

        if not messagebox.askyesno(
            "Confirm Restore",
            "This will replace your current academic records.\n\n"
            "A safety backup will be created first.\n\nContinue?"
        ):
            return

        try:
            safety_path = self.db.restore_backup(path)

            self.semesters = self.db.get_semesters()
            self.current_semester = self.semesters[0]

            self.refresh_data()
            self.show_page("Overview")

            messagebox.showinfo(
                "Restore Successful",
                f"Database restored successfully.\n\nSafety backup:\n{safety_path}"
            )

        except Exception as error:
            messagebox.showerror("Restore Failed", str(error))

    def show_database_location(self):

        messagebox.showinfo(
            "Database Location",
            self.db.database_name
        )

    # =====================================================
    # ABOUT
    # =====================================================

    def show_about(self):

        window = ctk.CTkToplevel(self.root)
        window.title("About CGPA Studio")
        window.geometry("420x430")
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()

        ctk.CTkLabel(
            window, text="CGPA STUDIO",
            font=("Segoe UI", 28, "bold"),
            text_color=self.TEXT
        ).pack(pady=(35, 5))

        ctk.CTkLabel(
            window, text=f"Version {self.VERSION}",
            text_color=self.BLUE,
            font=("Segoe UI", 13, "bold")
        ).pack()

        ctk.CTkLabel(
            window, text="Academic Performance Manager",
            text_color=self.MUTED
        ).pack(pady=10)

        ctk.CTkLabel(
            window, text="Built with Python, CustomTkinter and SQLite",
            text_color=self.MUTED
        ).pack(pady=8)

        ctk.CTkLabel(
            window, text="Made by",
            text_color=self.MUTED
        ).pack(pady=(25, 3))

        ctk.CTkLabel(
            window, text="Niranjan Sindu Das",
            font=("Segoe UI", 16, "bold"),
            text_color=self.TEXT
        ).pack()

        ctk.CTkLabel(
            window, text="© DAS & CO.",
            font=("Georgia", 22, "bold"),
            text_color="#FBBF24"
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            window, text="Created for learning and simply for fun.",
            text_color=self.MUTED,
            font=("Segoe UI", 10, "italic")
        ).pack(pady=5)

        ctk.CTkButton(
            window, text="Close",
            command=window.destroy, width=120
        ).pack(pady=15)


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    root = ctk.CTk()
    app = CGPAStudio(root)
    root.mainloop()
