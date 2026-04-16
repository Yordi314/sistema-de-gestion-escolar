from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

db = SQLAlchemy()

# Tabla Asociativa para la relación Muchos a Muchos entre User (Estudiante) y Course
# Incluye la calificación (nota) y fecha de calificación
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    student_id = db.Column(db.String, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey('courses.id'), primary_key=True)
    grade = db.Column(db.Float, nullable=True) # Calificación
    fecha_calificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Fecha de la última calificación
    
    # Relaciones
    student = db.relationship("User", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True) # e.g. "EST-01", "PRF-01"
    nombre = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False) # 'ADMIN', 'PROFESOR', 'ESTUDIANTE'

    # Relaciones
    courses_taught = db.relationship("Course", back_populates="professor", cascade="all, delete-orphan", lazy=True)
    enrollments = db.relationship("Enrollment", back_populates="student", cascade="all, delete-orphan", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.rol == 'ADMIN'

    def is_professor(self):
        return self.rol == 'PROFESOR'

    def is_student(self):
        return self.rol == 'ESTUDIANTE'

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String, primary_key=True) # e.g. "CUR-01"
    nombre = db.Column(db.String(100), nullable=False)
    profesor_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    # Relaciones
    professor = db.relationship("User", back_populates="courses_taught")
    enrollments = db.relationship("Enrollment", back_populates="course", cascade="all, delete-orphan", lazy=True)
