from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask
from flask_login import login_required, current_user
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

from .utils.utils import get_db_connection, paginador1, allowed_username


# Definir Blueprint
usuarios = Blueprint('usuarios', __name__)

@usuarios.route("/usuarios")
def usuariosBuscar():
    search_query = request.args.get('buscar', '', type=str)
    sql_count ='SELECT COUNT(*) FROM usuarios WHERE estado = true AND (nombre_usuario ILIKE %s OR correo_usuario ILIKE %s);'
    sql_lim ='SELECT * FROM usuarios WHERE estado = true AND (nombre_usuario ILIKE %s OR correo_usuario ILIKE %s) ORDER BY id_usuario DESC LIMIT %s OFFSET %s;'
    paginado = paginador1(sql_count,sql_lim,search_query,1,5)
    return render_template('usuarios/usuarios.html',
                           usuarios=paginado[0],
                           page=paginado[1],
                           per_page=paginado[2],
                           total_items=paginado[3],
                           total_pages=paginado[4],
                           search_query = search_query)



@usuarios.route("/usuarios/agregar")
def usuario_agregar():
    titulo = "Agregar usuario"
    return render_template('usuarios/usuarios_agregar.html',titulo = titulo)

@usuarios.route("/usuarios/agregar/nuevo", methods=('GET', 'POST'))
def usuario_nuevo():
    if request.method == 'POST':
        nombre_usuario= request.form['nombre_usuario']
        if allowed_username(nombre_usuario):
            apellido_mat = request.form['apellido_mat']
            apellido_pat = request.form['apellido_pat']
            correo_usuario = request.form['correo_usuario']
            contrasenia = request.form['contrasenia']
            Pass = generate_password_hash(contrasenia)
            estado = True
            fecha_creado= datetime.now()
            fecha_editado= datetime.now()
            
            con = get_db_connection()
            cur = con.cursor(cursor_factory=RealDictCursor)
            sql_validar="SELECT COUNT(*) FROM usuarios WHERE correo_usuario = '{}'".format(correo_usuario)
            cur.execute(sql_validar)
            existe = cur.fetchone()['count']
            if existe:
                cur.close()
                con.close()
                flash('Error: El correo seleccionado ya esta registrado. Intente con uno diferente')
                return redirect(url_for('usuarios.usuario_agregar'))
            else:
                sql="INSERT INTO usuarios (nombre_usuario, apellido_mat, apellido_pat, correo_usuario, contrasenia_usuario, estado, fecha_creado, fecha_editado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                valores=(nombre_usuario, apellido_mat, apellido_pat, correo_usuario, Pass, estado, fecha_creado, fecha_editado)
                cur.execute(sql,valores)
                con.commit()
                cur.close()
                con.close()
                flash('Usuario agregado correctamente')
                return redirect(url_for('usuarios.usuariosBuscar'))
            
        else:
            flash('Error: El correo no cuenta con las caracteristicas')
            return redirect(url_for('usuarios.usuario_agregar'))
    return redirect(url_for('usuarios.usuario_agregar'))

@usuarios.route('/usuarios/detalles/<int:id>')
def usuario_detalles(id):
    with get_db_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            # Asegúrate de usar parámetros para evitar inyección SQL
            cur.execute('SELECT * FROM usuarios WHERE id_usuario = %s', (id,))
            usuario = cur.fetchone()  # Recupera solo un registro
    if usuario is None:
        flash('El usuario no existe o ha sido eliminado.')
        return redirect(url_for('usuarios.usuariosBuscar'))
    return render_template('usuarios/usuario_detalles.html', usuario = usuario)

@usuarios.route('/usuarios/editar/<string:id>')
def usuario_editar(id):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id_usuario={0}'.format(id))
    usuario = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return render_template('usuarios/usuario_editar.html',usuario = usuario[0])

@usuarios.route('/usuarios/editar/<string:id>',methods=['POST'])
def usuario_actualizar(id):
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        apellido_mat = request.form['apellido_mat']
        apellido_pat = request.form['apellido_pat']
        correo_usuario = request.form['correo_usuario']
        contrasenia = request.form['contrasenia']
        Pass = generate_password_hash(contrasenia)        
        fecha_editado= datetime.now()
        
        con = get_db_connection()
        cur = con.cursor()
        sql="UPDATE usuarios SET nombre_usuario=%s,apellido_mat=%s,apellido_pat=%s,correo_usuario=%s,contrasenia_usuario=%s,fecha_editado=%s WHERE id_usuario=%s"
        valores=(nombre_usuario,apellido_mat,apellido_pat,correo_usuario,Pass,fecha_editado,id)
        cur.execute(sql,valores)
        con.commit()
        cur.close()
        con.close()
        flash("Usuario editado correctamente")
    return redirect(url_for('usuarios.usuariosBuscar'))

@usuarios.route('/usuarios/eliminar/<string:id>')
def usuario_eliminar(id):
    estado = False
    fecha_editado = datetime.now()
    con = get_db_connection()
    cur = con.cursor()
    sql = "UPDATE usuarios SET estado=%s,fecha_editado=%s WHERE id_usuario=%s"
    valores = (estado, fecha_editado, id)
    cur.execute(sql,valores)
    con.commit()
    cur.close()
    con.close()
    flash("Usuario eliminado correctamente")
    return redirect(url_for('usuarios.usuariosBuscar'))
# -------------------------------PAPELERA DE USUARIOS------------------------------------------------------

@usuarios.route("/usuarios/papelera")
def usuarios_papelera():
    search_query = request.args.get('buscar', '', type=str)
    sql_count ='SELECT COUNT(*) FROM usuarios WHERE estado = true AND (nombre_usuario ILIKE %s OR correo_usuario ILIKE %s);'
    sql_lim ='SELECT * FROM usuarios WHERE estado = false AND (nombre_usuario ILIKE %s OR correo_usuario ILIKE %s) ORDER BY id_usuario DESC LIMIT %s OFFSET %s;'
    paginado = paginador1(sql_count,sql_lim,search_query,1,5)
    return render_template('usuarios/usuariosPapelera.html',
                           usuarios=paginado[0],
                           page=paginado[1],
                           per_page=paginado[2],
                           total_items=paginado[3],
                           total_pages=paginado[4],
                           search_query = search_query)

@usuarios.route('/usuarios/papelera/detalles/<int:id>')
def usuario_detallesPapelera(id):
    with get_db_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            # Asegúrate de usar parámetros para evitar inyección SQL
            cur.execute('SELECT * FROM usuarios WHERE id_usuario = %s', (id,))
            usuario = cur.fetchone()  # Recupera solo un registro
    if usuario is None:
        flash('El usuario no existe o ha sido eliminado.')
        return redirect(url_for('usuarios.usuariosBuscar'))
    return render_template('usuarios/usuario_detallesPapelera.html', usuario = usuario)

@usuarios.route('/usuarios/papelera/restaurar/<string:id>')
def usuarios_restaurar(id):
    estado = True
    fecha_editado = datetime.now()
    con = get_db_connection()
    cur = con.cursor()
    sql = "UPDATE usuarios SET estado=%s,fecha_editado=%s WHERE id_usuario=%s"
    valores = (estado, fecha_editado, id)
    cur.execute(sql,valores)
    con.commit()
    cur.close()
    con.close()
    flash("Usuario restaurado correctamente")
    return redirect(url_for('usuarios.usuariosBuscar'))