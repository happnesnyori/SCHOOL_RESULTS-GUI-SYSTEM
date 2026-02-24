"""
models/result.py - Result ORM model with auto grade/GPA calculation
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from config import Base, GRADE_SCALE


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    marks = Column(Float, nullable=False)
    grade = Column(String(5), nullable=False)
    gpa = Column(Float, nullable=False)
    remarks = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
    )

    # Relationships
    student = relationship("Student", back_populates="results")
    subject = relationship("Subject", back_populates="results")

    @staticmethod
    def calculate_grade_gpa(marks: float):
        """Return (grade, gpa, remarks) for given marks."""
        for low, high, grade, gpa, remarks in GRADE_SCALE:
            if low <= marks <= high:
                return grade, gpa, remarks
        return "F", 0.0, "Fail"

    def __repr__(self):
        return f"<Result student={self.student_id} subject={self.subject_id} marks={self.marks} grade={self.grade}>"
