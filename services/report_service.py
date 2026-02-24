"""
services/report_service.py - PDF and CSV report generation
"""
import logging
import os
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from sqlalchemy.orm import Session
from models.result import Result
from models.student import Student
from models.subject import Subject
from models.class_model import Class

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def export_results_csv(self, filepath: str):
        """Export all results to CSV."""
        rows = (
            self.db.query(
                Student.admission_number,
                (Student.first_name + " " + Student.last_name).label("student_name"),
                Class.class_name,
                Subject.subject_name,
                Result.marks,
                Result.grade,
                Result.gpa,
                Result.remarks,
            )
            .join(Student, Result.student_id == Student.id)
            .outerjoin(Class, Student.class_id == Class.id)
            .join(Subject, Result.subject_id == Subject.id)
            .all()
        )
        df = pd.DataFrame(rows, columns=[
            "Admission No", "Student Name", "Class", "Subject",
            "Marks", "Grade", "GPA", "Remarks"
        ])
        df.to_csv(filepath, index=False)
        logger.info(f"CSV exported: {filepath}")
        return filepath

    def generate_student_report_card(self, student_id: int, filepath: str):
        """Generate PDF report card for a single student."""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError("Student not found.")

        results = (
            self.db.query(Result, Subject.subject_name)
            .join(Subject, Result.subject_id == Subject.id)
            .filter(Result.student_id == student_id)
            .all()
        )

        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            topMargin=1.5*cm, bottomMargin=1.5*cm,
            leftMargin=2*cm, rightMargin=2*cm,
        )
        styles = getSampleStyleSheet()
        story = []

        # Header
        title_style = ParagraphStyle(
            "Title", parent=styles["Title"],
            fontSize=18, textColor=colors.HexColor("#1a237e"),
            spaceAfter=6,
        )
        sub_style = ParagraphStyle(
            "Sub", parent=styles["Normal"],
            fontSize=11, textColor=colors.HexColor("#555555"),
            spaceAfter=4, alignment=1,
        )
        story.append(Paragraph("SCHOOL EXAMINATION RESULTS", title_style))
        story.append(Paragraph("Student Report Card", sub_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e")))
        story.append(Spacer(1, 0.4*cm))

        # Student info
        class_name = student.class_.class_name if student.class_ else "N/A"
        info_data = [
            ["Student Name:", student.full_name, "Admission No:", student.admission_number],
            ["Class:", class_name, "Gender:", student.gender],
            ["Date of Birth:", str(student.date_of_birth or "N/A"), "Date Generated:", datetime.now().strftime("%Y-%m-%d")],
        ]
        info_table = Table(info_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.5*cm))

        # Results table
        table_data = [["#", "Subject", "Marks", "Grade", "GPA", "Remarks"]]
        total_marks = 0
        total_gpa = 0
        for i, (result, subject_name) in enumerate(results, 1):
            table_data.append([
                str(i), subject_name,
                f"{result.marks:.1f}", result.grade,
                f"{result.gpa:.1f}", result.remarks,
            ])
            total_marks += result.marks
            total_gpa += result.gpa

        if results:
            avg_marks = total_marks / len(results)
            avg_gpa = total_gpa / len(results)
            table_data.append(["", "AVERAGE", f"{avg_marks:.1f}", "", f"{avg_gpa:.2f}", ""])

        t = Table(table_data, colWidths=[1*cm, 5*cm, 2.5*cm, 2*cm, 2*cm, 4*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.HexColor("#f5f5f5"), colors.white]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8eaf6")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            "This report card was generated automatically by the School Examination Results Management System.",
            ParagraphStyle("footer", parent=styles["Normal"], fontSize=8,
                           textColor=colors.grey, alignment=1)
        ))

        doc.build(story)
        logger.info(f"Report card generated: {filepath}")
        return filepath

    def generate_class_report_pdf(self, class_id: int, filepath: str):
        """Generate PDF report for an entire class."""
        cls = self.db.query(Class).filter(Class.id == class_id).first()
        if not cls:
            raise ValueError("Class not found.")

        students = (
            self.db.query(Student)
            .filter(Student.class_id == class_id)
            .order_by(Student.first_name)
            .all()
        )

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                topMargin=1.5*cm, bottomMargin=1.5*cm,
                                leftMargin=2*cm, rightMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "Title", parent=styles["Title"],
            fontSize=16, textColor=colors.HexColor("#1a237e"), spaceAfter=4,
        )
        story.append(Paragraph(f"CLASS PERFORMANCE REPORT — {cls.class_name}", title_style))
        story.append(Paragraph(f"Academic Year: {cls.academic_year}", styles["Normal"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a237e")))
        story.append(Spacer(1, 0.5*cm))

        table_data = [["Adm No", "Student Name", "Subjects", "Avg Marks", "Avg GPA", "Div"]]
        for student in students:
            results = self.db.query(Result).filter(Result.student_id == student.id).all()
            if results:
                avg_marks = sum(r.marks for r in results) / len(results)
                avg_gpa = sum(r.gpa for r in results) / len(results)
                _, _, remarks = Result.calculate_grade_gpa(avg_marks)
            else:
                avg_marks = avg_gpa = 0
                remarks = "N/A"
            table_data.append([
                student.admission_number,
                student.full_name,
                str(len(results)),
                f"{avg_marks:.1f}",
                f"{avg_gpa:.2f}",
                remarks,
            ])

        t = Table(table_data, colWidths=[2.5*cm, 5*cm, 2*cm, 2.5*cm, 2.5*cm, 3*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        doc.build(story)
        logger.info(f"Class report generated: {filepath}")
        return filepath
