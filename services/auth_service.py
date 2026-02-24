"""
services/auth_service.py - Authentication and authorization service
"""
import bcrypt
import logging
from sqlalchemy.orm import Session
from models.user import Admin, Teacher

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    def login(self, email: str, password: str):
        """Return (user_object, role) or (None, None)."""
        email = email.strip().lower()

        admin = self.db.query(Admin).filter(Admin.email == email).first()
        if admin and self.verify_password(password, admin.password_hash):
            logger.info(f"Admin login: {email}")
            return admin, "ADMIN"

        teacher = self.db.query(Teacher).filter(Teacher.email == email).first()
        if teacher and self.verify_password(password, teacher.password_hash):
            logger.info(f"Teacher login: {email}")
            return teacher, "TEACHER"

        logger.warning(f"Failed login attempt for: {email}")
        return None, None

    def create_admin(self, full_name: str, email: str, password: str) -> Admin:
        email = email.strip().lower()
        if self.db.query(Admin).filter(Admin.email == email).first():
            raise ValueError("Admin with this email already exists.")
        admin = Admin(
            full_name=full_name,
            email=email,
            password_hash=self.hash_password(password),
        )
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        return admin

    def seed_default_admin(self):
        """Create default admin if none exists."""
        if not self.db.query(Admin).first():
            self.create_admin("System Administrator", "admin@school.edu", "Admin@1234")
            logger.info("Default admin seeded: admin@school.edu / Admin@1234")
