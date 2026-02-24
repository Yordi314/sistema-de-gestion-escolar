from flask import Flask, render_template, request, redirect, url_for, flash
import os
from database import db
from models import Student, Professor

app = Flask(__name__)
# Secret key needed for flash messages
app.secret_key = "secreto-super-seguro-mvp"

# ================================
# FILTROS DE PLANTILLA (Jinja2)
# ================================
@app.template_filter('is_professor')
def is_professor(user):
    return isinstance(user, Professor)

@app.template_filter('is_student')
def is_student(user):
    return isinstance(user, Student)

# ================================
# RUTAS DE LA APLICACIÓN
# ================================

@app.route("/")
def index():
    """Página de inicio (Simulación de login)."""
    return render_template("index.html")

# --------------------------------
# VISTAS DE ADMINISTRADOR
# --------------------------------

@app.route("/admin/dashboard")
def admin_dashboard():
    """Panel principal del administrador."""
    users = db.users.values()
    courses = db.courses.values()
    return render_template("admin_dashboard.html", users=users, courses=courses)

@app.route("/admin/usuarios")
def admin_lista_usuarios():
    """HU Extras - Vista dedicada de todos los usuarios con buscador."""
    users = db.users.values()
    return render_template("admin_lista_usuarios.html", users=users)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    """HU01 - Alta de Usuarios"""
    if request.method == "POST":
        rol = request.form.get("rol")
        uid = request.form.get("uid")
        nombre = request.form.get("nombre")
        
        try:
            db.add_user(rol, uid, nombre)
            flash(f"Usuario {nombre} ({rol}) creado con éxito.", "success")
            return redirect(url_for('admin_dashboard'))
        except ValueError as e:
            flash(str(e), "danger")
            
    return render_template("admin_forms/registro.html")

@app.route("/cursos/nuevo", methods=["GET", "POST"])
def crear_curso():
    """HU02 - Creación de Cursos"""
    if request.method == "POST":
        cid = request.form.get("cid")
        nombre = request.form.get("nombre")
        prof_id = request.form.get("prof_id")
        
        try:
            db.add_course(cid, nombre, prof_id)
            flash(f"Curso {nombre} creado correctamente.", "success")
            return redirect(url_for('admin_dashboard'))
        except ValueError as e:
            flash(str(e), "danger")
            
    # GET: Pasar lista de profesores al formulario
    profesores = [u for u in db.users.values() if isinstance(u, Professor)]
    return render_template("admin_forms/curso.html", profesores=profesores)

@app.route("/cursos/<cid>/inscribir", methods=["GET", "POST"])
def inscribir_estudiante(cid):
    """HU03 - Inscripción de Estudiantes a un Curso"""
    curso = db.get_course(cid)
    if not curso:
        flash("Curso no encontrado.", "danger")
        return redirect(url_for('admin_dashboard'))
        
    if request.method == "POST":
        estudiantes_ids = request.form.getlist("estudiantes")
        exitos = 0
        for sid in estudiantes_ids:
            try:
                db.enroll_student(cid, sid)
                exitos += 1
            except ValueError as e:
                flash(str(e), "warning")
        
        if exitos > 0:
            flash(f"{exitos} estudiante(s) inscrito(s) correctamente.", "success")
        return redirect(url_for('admin_dashboard'))
        
    # GET: Listar estudiantes que AÚN NO están en el curso
    todos_estudiantes = [u for u in db.users.values() if isinstance(u, Student)]
    disponibles = [e for e in todos_estudiantes if e.id not in curso.student_ids]
    
    return render_template("admin_forms/inscribir.html", curso=curso, estudiantes=disponibles)

# --------------------------------
# VISTAS DE PROFESOR
# --------------------------------

@app.route("/profesor/dashboard", methods=["GET", "POST"])
def profesor_dashboard():
    """HU04 - Panel del Profesor (Calificaciones)"""
    # GET: Formulario inicial simulando el logueo
    profesores = [u for u in db.users.values() if isinstance(u, Professor)]
    
    if request.method == "POST":
        # Acción 1: Seleccionar perfil
        if "action" in request.form and request.form["action"] == "ingresar":
            prof_id = request.form.get("prof_id")
            return redirect(url_for('profesor_vista_cursos', prof_id=prof_id))
            
    return render_template("profesor/ingreso.html", profesores=profesores)

@app.route("/profesor/<prof_id>/cursos", methods=["GET", "POST"])
def profesor_vista_cursos(prof_id):
    """HU04 - Vista de Gestión de Notas del Profesor"""
    prof = db.get_user(prof_id)
    if not prof or not isinstance(prof, Professor):
        flash("Acceso denegado.", "danger")
        return redirect(url_for('index'))
        
    mis_cursos = [c for c in db.courses.values() if c.professor_id == prof_id]
    
    if request.method == "POST":
        # Acción 2: Guardar nota
        cid = request.form.get("course_id")
        sid = request.form.get("student_id")
        nota = float(request.form.get("nota"))
        
        try:
            db.assign_grade(cid, prof_id, sid, nota)
            flash("Calificación guardada.", "success")
        except ValueError as e:
            flash(str(e), "danger")
            
        return redirect(url_for('profesor_vista_cursos', prof_id=prof_id))
        
    return render_template("profesor/dashboard.html", profesor=prof, cursos=mis_cursos, get_student=db.get_user)

# --------------------------------
# VISTAS DE ESTUDIANTE
# --------------------------------

@app.route("/estudiante/dashboard", methods=["GET", "POST"])
def estudiante_dashboard():
    """HU05 - Panel del Estudiante (Boletín)"""
    estudiantes = [u for u in db.users.values() if isinstance(u, Student)]
    
    if request.method == "POST":
        sid = request.form.get("student_id")
        try:
            reporte = db.get_student_report(sid)
            return render_template("estudiante/reporte.html", reporte=reporte)
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for('estudiante_dashboard'))
            
    return render_template("estudiante/ingreso.html", estudiantes=estudiantes)

# ================================
# EJECUCIÓN
# ================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
