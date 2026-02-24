"""
models/class_model.py - Class ORM model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from config import Base


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(80), nullable=False)
    academic_year = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    students = relationship("Student", back_populates="class_", lazy="select")
    subjects = relationship("Subject", back_populates="class_", lazy="select")

    def __repr__(self):
        return f"<Class id={self.id} name={self.class_name} year={self.academic_year}>"
