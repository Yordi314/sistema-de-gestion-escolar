class User:
    """Clase base abstracta para todos los usuarios del sistema MVC.
    Define las propiedades comunes como el ID y el nombre.
    """
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def to_dict(self):
        """Serializa la instancia a un diccionario para guardarlo en JSON."""
        return {"id": self.id, "name": self.name, "role": self.__class__.__name__}

    @classmethod
    def from_dict(cls, data: dict):
        """Deserializa un diccionario instanciando el objeto base."""
        return cls(data["id"], data["name"])


class Student(User):
    """Representa a un estudiante. Extiende la clase base User."""
    def __init__(self, id: str, name: str):
        super().__init__(id, name)


class Professor(User):
    """Representa a un profesor. Extiende la clase base User."""
    def __init__(self, id: str, name: str):
        super().__init__(id, name)


class UserFactory:
    """Implementación del patrón Factory Method (Fábrica de Usuarios).
    
    Principio: Centraliza la creación de los objetos de tipo User (Estudiante, Profesor).
    Esto aísla la lógica de instanciación del cliente (p.ej. el Controlador Flask 
    solo necesita pasar los datos del <form> HTML y obtener el objeto correcto), 
    lo que facilita agregar nuevos roles sin alterar enrutadores HTTP.
    """
    @staticmethod
    def create_user(role: str, id: str, name: str) -> User:
        """Crea una instancia de Student o Professor basado en la cadena del rol."""
        role = role.upper()
        if role == "ESTUDIANTE" or role == "STUDENT":
            return Student(id, name)
        elif role == "PROFESOR" or role == "PROFESSOR":
            return Professor(id, name)
        else:
            raise ValueError(f"Rol desconocido: {role}")
            
    @staticmethod
    def from_dict(data: dict) -> User:
        """Helper para recrear el usuario correcto a partir de un dict cargado del JSON."""
        return UserFactory.create_user(data.get("role", "ESTUDIANTE"), data["id"], data["name"])


class Course:
    """Clase que representa un Curso en el sistema.
    Mantiene referencias a su profesor, estudiantes inscritos y sus calificaciones.
    """
    def __init__(self, id: str, name: str, professor_id: str):
        self.id = id
        self.name = name
        self.professor_id = professor_id
        self.student_ids = []
        self.grades = {}  # type: dict[str, float]

    def to_dict(self):
        """Serializa el curso a un diccionario."""
        return {
            "id": self.id,
            "name": self.name,
            "professor_id": self.professor_id,
            "student_ids": self.student_ids,
            "grades": self.grades
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        """Reconstruye la instancia del Curso a partir de un diccionario."""
        course = cls(data["id"], data["name"], data["professor_id"])
        course.student_ids = data.get("student_ids", [])
        course.grades = data.get("grades", {})
        return course
