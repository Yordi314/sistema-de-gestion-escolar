import os
import json
from models import User, Course, Student, Professor, UserFactory

DB_FILE = "data.json"

class Database:
    """Implementación del patrón Singleton (Gestor de Estado/Base de Datos).
    
    Principio: Garantiza que a lo largo de toda la ejecución de la aplicación Flask 
    (sirviendo peticiones GET y POST concurrentes) solo exista una única instancia.
    
    Esta clase también asume el rol de 'Capa de Negocio', aplicando validaciones
    antes de mutar el diccionario en memoria y volcándolo automáticamente a JSON.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls, *args, **kwargs)
            cls._instance.users = {}  # {id: User object}
            cls._instance.courses = {} # {id: Course object}
            cls._instance.load() # Cargar desde data.json si existe
        return cls._instance

    def load(self):
        """Carga el estado del sistema desde el archivo local data.json."""
        # Se asegura de crear el archivo desde la ruta donde está corriendo Flask
        file_path = os.path.join(os.path.dirname(__file__), DB_FILE)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    for uid, udata in data.get("users", {}).items():
                        self.users[uid] = UserFactory.from_dict(udata)
                        
                    for cid, cdata in data.get("courses", {}).items():
                        self.courses[cid] = Course.from_dict(cdata)
            except Exception as e:
                print(f"Error cargando base de datos: {e}")
                
        # Si no hay usuarios una vez cargado (o si hubo error/no existía), inyectamos datos demo
        if not self.users:
            self._seed_demo_data()

    def _seed_demo_data(self):
        """Genera datos de demostración para el sistema."""
        print("Generando datos demo...")
        
        usuarios_demo = [
            UserFactory.create_user("professor", "PRF-01", "Dra. Ada Lovelace"),
            UserFactory.create_user("professor", "PRF-02", "Dr. Alan Turing"),
            UserFactory.create_user("student", "EST-01", "Juan Pérez"),
            UserFactory.create_user("student", "EST-02", "María García"),
            UserFactory.create_user("student", "EST-03", "Carlos López"),
        ]
        for u in usuarios_demo:
            self.users[u.id] = u
            
        cursos_demo = [
            Course("CUR-01", "Introducción a la Programación", "PRF-01"),
            Course("CUR-02", "Estructuras de Datos", "PRF-02"),
            Course("CUR-03", "Ingeniería de Software", "PRF-01"),
        ]
        for c in cursos_demo:
            self.courses[c.id] = c
            
        # Inscripciones
        self.courses["CUR-01"].student_ids.extend(["EST-01", "EST-02"])
        self.courses["CUR-02"].student_ids.extend(["EST-02", "EST-03"])
        self.courses["CUR-03"].student_ids.extend(["EST-01", "EST-03"])
        
        # Calificaciones
        self.courses["CUR-01"].grades["EST-01"] = 95.0
        self.courses["CUR-01"].grades["EST-02"] = 88.0
        self.courses["CUR-02"].grades["EST-02"] = 92.0
        
        self.save()
        print("Datos demo generados exitosamente.")

    def save(self):
        """Serializa y guarda el estado actual del sistema en data.json."""
        file_path = os.path.join(os.path.dirname(__file__), DB_FILE)
        data = {
            "users": {uid: u.to_dict() for uid, u in self.users.items()},
            "courses": {cid: c.to_dict() for cid, c in self.courses.items()}
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ==========================
    # BUSINESS LOGIC METHODS
    # ==========================

    def add_user(self, role: str, user_id: str, name: str) -> User:
        """HU01: Valida ID único, crea por Factory y guarda."""
        if user_id in self.users:
            raise ValueError(f"Ya existe un usuario registrado con la cédula/ID {user_id}")
            
        user = UserFactory.create_user(role, user_id, name)
        self.users[user.id] = user
        self.save()
        return user

    def get_user(self, user_id: str) -> User:
        return self.users.get(user_id)

    def add_course(self, course_id: str, name: str, professor_id: str) -> Course:
        """HU02: Crea un curso validando que el profesor exista."""
        if course_id in self.courses:
            raise ValueError(f"El código del curso {course_id} ya se encuentra en uso.")
            
        professor = self.get_user(professor_id)
        if not professor or not isinstance(professor, Professor):
            raise ValueError("El profesor seleccionado no es válido o no existe.")

        course = Course(course_id, name, professor_id)
        self.courses[course.id] = course
        self.save()
        return course

    def get_course(self, course_id: str) -> Course:
        return self.courses.get(course_id)

    def enroll_student(self, course_id: str, student_id: str) -> bool:
        """HU03: Verifica existencia de ambos y que no haya duplicidad."""
        course = self.get_course(course_id)
        if not course:
            raise ValueError(f"Curso no encontrado.")
            
        student = self.get_user(student_id)
        if not student or not isinstance(student, Student):
            raise ValueError("Estudiante seleccionado inválido.")
            
        if student_id in course.student_ids:
            raise ValueError(f"El estudiante {student.name} ya está en este curso.")
            
        course.student_ids.append(student_id)
        self.save()
        return True

    def assign_grade(self, course_id: str, professor_id: str, student_id: str, grade: float) -> bool:
        """HU04: Asigna notas desde el Dashboard del Profesor."""
        course = self.get_course(course_id)
        if not course:
            raise ValueError("Curso no encontrado.")
            
        if course.professor_id != professor_id:
            raise ValueError("Aviso de Seguridad: Solo el titular del curso puede calificar.")
            
        if student_id not in course.student_ids:
            raise ValueError("Este estudiante no cursa tu materia.")
            
        if not (0 <= grade <= 100):
            raise ValueError("Las calificaciones del Colegio San Ignacio deben ser sobre 100 puntos.")
            
        course.grades[student_id] = grade
        self.save()
        return True

    def get_student_report(self, student_id: str) -> dict:
        """HU05: Consolida el boletín recorriendo los cursos."""
        student = self.get_user(student_id)
        if not student or not isinstance(student, Student):
            raise ValueError("Error leyendo el perfil de estudiante.")
            
        report = {
            "estudiante": student.name,
            "id": student.id,
            "cursos": []
        }
        
        for course in self.courses.values():
            if student_id in course.student_ids:
                # Retorna 'N/A' si el profesor no le ha puesto nota
                grade = course.grades.get(student_id, "N/A") 
                report["cursos"].append({
                    "curso_id": course.id,
                    "curso_nombre": course.name,
                    "calificacion": grade
                })
        return report

# Instancia global exportable para los controladores Flask
db = Database()
