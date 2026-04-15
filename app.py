from flask import Flask, render_template, request, redirect, url_for, flash
import os
from models import db, User, Course, Enrollment
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = "secreto-super-seguro-mvp"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
login_manager.login_message = "Acceso Denegado. Por favor inicie sesión."
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def seed_db():
    db.create_all()
    if not User.query.first():
        print("Generando datos demo...")
        users_demo = [
            User(id="ADM-01", nombre="Admin Sistema", rol="ADMIN"),
            User(id="PRF-01", nombre="Dra. Ada Lovelace", rol="PROFESOR"),
            User(id="PRF-02", nombre="Dr. Alan Turing", rol="PROFESOR"),
            User(id="EST-01", nombre="Juan Pérez", rol="ESTUDIANTE"),
            User(id="EST-02", nombre="María García", rol="ESTUDIANTE"),
            User(id="EST-03", nombre="Carlos López", rol="ESTUDIANTE")
        ]
        for u in users_demo:
            u.set_password("123456")
            db.session.add(u)
            
        cursos_demo = [
            Course(id="CUR-01", nombre="Introducción a la Programación", profesor_id="PRF-01"),
            Course(id="CUR-02", nombre="Estructuras de Datos", profesor_id="PRF-02"),
            Course(id="CUR-03", nombre="Ingeniería de Software", profesor_id="PRF-01"),
        ]
        for c in cursos_demo:
            db.session.add(c)
            
        db.session.commit()
        
        enrolls = [
            Enrollment(course_id="CUR-01", student_id="EST-01", grade=95.0),
            Enrollment(course_id="CUR-01", student_id="EST-02", grade=88.0),
            Enrollment(course_id="CUR-02", student_id="EST-02", grade=92.0),
            Enrollment(course_id="CUR-02", student_id="EST-03", grade=None),
            Enrollment(course_id="CUR-03", student_id="EST-01", grade=None),
            Enrollment(course_id="CUR-03", student_id="EST-03", grade=None),
        ]
        for e in enrolls:
            db.session.add(e)
        db.session.commit()

@app.template_filter('is_professor')
def is_professor(user):
    return user.rol == 'PROFESOR' if user else False

@app.template_filter('is_student')
def is_student(user):
    return user.rol == 'ESTUDIANTE' if user else False

@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        if current_user.rol == 'ADMIN':
            return redirect(url_for('admin_dashboard'))
        elif current_user.rol == 'PROFESOR':
            return redirect(url_for('profesor_vista_cursos', prof_id=current_user.id))
        elif current_user.rol == 'ESTUDIANTE':
            return redirect(url_for('estudiante_dashboard'))
            
    if request.method == "POST":
        uid = request.form.get("uid")
        password = request.form.get("password")
        user = User.query.get(uid)
        
        if user and user.check_password(password):
            login_user(user)
            flash(f"Bienvenido {user.nombre}!", "success")
            if user.rol == 'ADMIN':
                return redirect(url_for('admin_dashboard'))
            elif user.rol == 'PROFESOR':
                return redirect(url_for('profesor_vista_cursos', prof_id=current_user.id))
            elif user.rol == 'ESTUDIANTE':
                return redirect(url_for('estudiante_dashboard'))
        else:
            flash("Credenciales inválidas", "danger")
            
    return render_template("index.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for('index'))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash("Acceso Denegado.", "danger")
        return redirect(url_for('index'))
        
    users = User.query.all()
    
    q_course = request.args.get("q_course", "")
    page_course = request.args.get("page_course", 1, type=int)
    course_query = Course.query
    if q_course:
        search = f"%{q_course}%"
        course_query = course_query.filter(db.or_(
            Course.nombre.ilike(search),
            Course.id.ilike(search)
        ))
    courses_pagination = course_query.paginate(page=page_course, per_page=10, error_out=False)
    
    return render_template("admin_dashboard.html", users=users, courses_pagination=courses_pagination, q_course=q_course)

@app.route("/admin/usuarios")
@login_required
def admin_lista_usuarios():
    if not current_user.is_admin():
        flash("Acceso Denegado.", "danger")
        return redirect(url_for('index'))
        
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    
    query = User.query
    if q:
        search = f"%{q}%"
        query = query.filter(db.or_(
            User.nombre.ilike(search),
            User.id.ilike(search),
            User.rol.ilike(search)
        ))
        
    users_pagination = query.paginate(page=page, per_page=10, error_out=False)
    return render_template("admin_lista_usuarios.html", users_pagination=users_pagination, q=q)

@app.route("/registro", methods=["GET", "POST"])
@login_required
def registro():
    if not current_user.is_admin():
        flash("Acceso Denegado.", "danger")
        return redirect(url_for('index'))
        
    if request.method == "POST":
        rol = request.form.get("rol")
        uid = request.form.get("uid")
        nombre = request.form.get("nombre")
        password = request.form.get("password") or "123456"
        
        if User.query.get(uid):
            flash(f"Ya existe un usuario con el ID {uid}", "danger")
        else:
            user = User(id=uid, nombre=nombre, rol=rol)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f"Usuario {nombre} ({rol}) creado con éxito.", "success")
            return redirect(url_for('admin_dashboard'))
            
    return render_template("admin_forms/registro.html")

@app.route("/cursos/nuevo", methods=["GET", "POST"])
@login_required
def crear_curso():
    if not current_user.is_admin():
        flash("Acceso Denegado.", "danger")
        return redirect(url_for('index'))
        
    if request.method == "POST":
        cid = request.form.get("cid")
        nombre = request.form.get("nombre")
        prof_id = request.form.get("prof_id")
        
        if Course.query.get(cid):
            flash(f"El curso {cid} ya existe.", "danger")
        elif not User.query.get(prof_id) or User.query.get(prof_id).rol != 'PROFESOR':
            flash("Profesor inválido.", "danger")
        else:
            curso = Course(id=cid, nombre=nombre, profesor_id=prof_id)
            db.session.add(curso)
            db.session.commit()
            flash(f"Curso {nombre} creado correctamente.", "success")
            return redirect(url_for('admin_dashboard'))
            
    profesores = User.query.filter_by(rol='PROFESOR').all()
    return render_template("admin_forms/curso.html", profesores=profesores)

@app.route("/cursos/<cid>/inscribir", methods=["GET", "POST"])
@login_required
def inscribir_estudiante(cid):
    if not current_user.is_admin():
        flash("Acceso Denegado.", "danger")
        return redirect(url_for('index'))
        
    curso = Course.query.get(cid)
    if not curso:
        flash("Curso no encontrado.", "danger")
        return redirect(url_for('admin_dashboard'))
        
    if request.method == "POST":
        estudiantes_ids = request.form.getlist("estudiantes")
        exitos = 0
        for sid in estudiantes_ids:
            if not Enrollment.query.filter_by(student_id=sid, course_id=cid).first():
                enroll = Enrollment(student_id=sid, course_id=cid)
                db.session.add(enroll)
                exitos += 1
        
        if exitos > 0:
            db.session.commit()
            flash(f"{exitos} estudiante(s) inscrito(s) correctamente.", "success")
        return redirect(url_for('admin_dashboard'))
        
    subquery = db.session.query(Enrollment.student_id).filter_by(course_id=cid)
    disponibles = User.query.filter(User.rol == 'ESTUDIANTE', ~User.id.in_(subquery)).all()
    
    return render_template("admin_forms/inscribir.html", curso=curso, estudiantes=disponibles)

@app.route("/profesor/<prof_id>/cursos", methods=["GET", "POST"])
@login_required
def profesor_vista_cursos(prof_id):
    if current_user.rol != 'PROFESOR' or current_user.id != prof_id:
        flash("Acceso denegado.", "danger")
        return redirect(url_for('index'))
        
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    
    query = Course.query.filter_by(profesor_id=prof_id)
    if q:
        search = f"%{q}%"
        query = query.filter(db.or_(
            Course.nombre.ilike(search),
            Course.id.ilike(search)
        ))
        
    cursos_pagination = query.paginate(page=page, per_page=10, error_out=False)
    
    if request.method == "POST":
        cid = request.form.get("course_id")
        sid = request.form.get("student_id")
        nota = request.form.get("nota")
        
        try:
            nota = float(nota)
            enroll = Enrollment.query.filter_by(student_id=sid, course_id=cid).first()
            if enroll and enroll.course.profesor_id == prof_id:
                enroll.grade = nota
                db.session.commit()
                flash("Calificación guardada.", "success")
            else:
                flash("Error al asignar calificación.", "danger")
        except ValueError:
            flash("Calificación inválida.", "danger")
            
        return redirect(url_for('profesor_vista_cursos', prof_id=prof_id, q=q, page=page))
        
    def get_student(sid):
        return User.query.get(sid)
        
    return render_template("profesor/dashboard.html", profesor=current_user, cursos_pagination=cursos_pagination, get_student=get_student, q=q)

@app.route("/estudiante/dashboard")
@login_required
def estudiante_dashboard():
    if current_user.rol != 'ESTUDIANTE':
        flash("Acceso denegado.", "danger")
        return redirect(url_for('index'))
        
    reporte = {
        "estudiante": current_user.nombre,
        "id": current_user.id,
        "cursos": []
    }
    
    for enroll in current_user.enrollments:
        reporte["cursos"].append({
            "curso_id": enroll.course.id,
            "curso_nombre": enroll.course.nombre,
            "calificacion": enroll.grade if enroll.grade is not None else "N/A"
        })
        
    return render_template("estudiante/reporte.html", reporte=reporte)

with app.app_context():
    seed_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
