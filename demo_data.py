from app import app, db, User, Course, Enrollment

def run_demo_data():
    with app.app_context():
        print("Limpiando la base de datos...")
        db.drop_all()
        db.create_all()

        print("Generando Administradores...")
        admin1 = User(id="ADM-01", nombre="Yordi Polanco", rol="ADMIN")
        admin1.set_password("123456")
        admin2 = User(id="ADM-02", nombre="Directora Maria", rol="ADMIN")
        admin2.set_password("123456")
        db.session.add_all([admin1, admin2])

        print("Generando Profesores...")
        prof1 = User(id="PRF-01", nombre="Roberto Gómez", rol="PROFESOR")
        prof1.set_password("123456")
        prof2 = User(id="PRF-02", nombre="Ana Martínez", rol="PROFESOR")
        prof2.set_password("123456")
        prof3 = User(id="PRF-03", nombre="Carlos Ruiz", rol="PROFESOR")
        prof3.set_password("123456")
        prof4 = User(id="PRF-04", nombre="Beatriz Solórzano", rol="PROFESOR")
        prof4.set_password("123456")
        db.session.add_all([prof1, prof2, prof3, prof4])

        print("Generando Estudiantes Masivos...")
        estudiantes = []
        nombres = [
            "Juan Pérez", "María García", "Luis Fernández", "Ana López",
            "Carlos Gómez", "Laura Díaz", "Pedro Sánchez", "Sofía Vargas",
            "Camila Herrera", "Diego Alvarado", "Valentina Rojas", "Andrés Castro",
            "Martina Silva", "Sebastián Reyes", "Lucía Morales", "Mateo Espinosa",
            "Valeria Romero", "Joaquín Mendoza", "Isabella Navarro", "Javier Soto"
        ]
        for i, nombre in enumerate(nombres):
            est = User(id=f"EST-{i+1:02d}", nombre=nombre, rol="ESTUDIANTE")
            est.set_password("123456")
            estudiantes.append(est)
        db.session.add_all(estudiantes)
        db.session.commit()

        print("Generando Cursos...")
        c1 = Course(id="CUR-01", nombre="Matemáticas Avanzadas", profesor_id="PRF-01")
        c2 = Course(id="CUR-02", nombre="Física I", profesor_id="PRF-01")
        c3 = Course(id="CUR-03", nombre="Literatura Contemporánea", profesor_id="PRF-02")
        c4 = Course(id="CUR-04", nombre="Historia Universal", profesor_id="PRF-03")
        c5 = Course(id="CUR-05", nombre="Química Orgánica", profesor_id="PRF-04")
        c6 = Course(id="CUR-06", nombre="Lógica y Algoritmos", profesor_id="PRF-01")
        db.session.add_all([c1, c2, c3, c4, c5, c6])
        db.session.commit()

        print("Generando Matrículas y Evaluaciones...")
        enrollments_list = []
        
        # Matematica (PRF-01)
        enrollments_list.extend([
            Enrollment(student_id="EST-01", course_id="CUR-01", grade=85.5),
            Enrollment(student_id="EST-02", course_id="CUR-01", grade=90.0),
            Enrollment(student_id="EST-03", course_id="CUR-01", grade=None),
            Enrollment(student_id="EST-04", course_id="CUR-01", grade=60.0),
            Enrollment(student_id="EST-05", course_id="CUR-01", grade=78.2),
            Enrollment(student_id="EST-06", course_id="CUR-01", grade=99.0),
        ])
        
        # Fisica (PRF-01) 
        enrollments_list.extend([
            Enrollment(student_id="EST-07", course_id="CUR-02", grade=78.0),
            Enrollment(student_id="EST-08", course_id="CUR-02", grade=None),
            Enrollment(student_id="EST-09", course_id="CUR-02", grade=88.5),
            Enrollment(student_id="EST-10", course_id="CUR-02", grade=72.0),
            Enrollment(student_id="EST-11", course_id="CUR-02", grade=69.0),
        ])

        # Literatura (PRF-02) 
        enrollments_list.extend([
            Enrollment(student_id="EST-01", course_id="CUR-03", grade=None),
            Enrollment(student_id="EST-12", course_id="CUR-03", grade=95.0),
            Enrollment(student_id="EST-13", course_id="CUR-03", grade=84.0),
            Enrollment(student_id="EST-14", course_id="CUR-03", grade=91.5),
        ])

        # Historia (PRF-03)
        enrollments_list.extend([
            Enrollment(student_id="EST-15", course_id="CUR-04", grade=82.0),
            Enrollment(student_id="EST-16", course_id="CUR-04", grade=79.0),
            Enrollment(student_id="EST-17", course_id="CUR-04", grade=None),
        ])
        
        # Quimica (PRF-04)
        enrollments_list.extend([
            Enrollment(student_id="EST-18", course_id="CUR-05", grade=58.0),
            Enrollment(student_id="EST-19", course_id="CUR-05", grade=90.0),
            Enrollment(student_id="EST-20", course_id="CUR-05", grade=92.5),
            Enrollment(student_id="EST-01", course_id="CUR-05", grade=80.0),
        ])

        # Logica (PRF-01) (Muchos pendientes)
        enrollments_list.extend([
            Enrollment(student_id="EST-01", course_id="CUR-06", grade=None),
            Enrollment(student_id="EST-02", course_id="CUR-06", grade=None),
            Enrollment(student_id="EST-03", course_id="CUR-06", grade=100.0),
            Enrollment(student_id="EST-15", course_id="CUR-06", grade=None),
        ])
        
        db.session.add_all(enrollments_list)
        db.session.commit()

        print("¡Datos Masivos generados con éxito!")

if __name__ == "__main__":
    run_demo_data()
