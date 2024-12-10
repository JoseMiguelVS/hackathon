from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask,make_response
from flask_login import login_required, current_user
from fpdf import FPDF
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
import json  # Importar el módulo json


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

@usuarios.route('/informacionDocumentada')
def infoDocu():
    return render_template('informacionDocumentada/index.html')

@usuarios.route('/guardar_documento', methods=['POST'])
def guardar_documento():
    # Obtener los datos del formulario. Cada campo está dentro de un array debido al índice
    documentos = request.form.getlist('documentos[0][codigoDocumento]')
    revision = request.form.getlist('documentos[0][numeroRevision]')
    fecha_emision = request.form.getlist('documentos[0][fechaEmision]')
    fecha_revision = request.form.getlist('documentos[0][fechaRevision]')
    
    # Crear un array de diccionarios con los datos obtenidos
    documentos_data = []
    for i in range(len(documentos)):
        documento = {
            'codigoDocumento': documentos[i],
            'numeroRevision': revision[i],
            'fechaEmision': fecha_emision[i],
            'fechaRevision': fecha_revision[i]
        }
        documentos_data.append(documento)
    
    # Convertir el array de diccionarios a una cadena JSON
    documentos_json = json.dumps(documentos_data)
    
    # Insertar los datos en la base de datos
    con = get_db_connection()
    cur = con.cursor()
    
    # Usa comillas dobles si "array" es una columna reservada
    sql = 'INSERT INTO documentos ("array") VALUES (%s)'
    valores = (documentos_json,)
    cur.execute(sql, valores)
    
    con.commit()
    cur.close()
    con.close()
    
    flash('Documento guardado correctamente')
    return redirect(url_for('usuarios.infoDocu'))

# @usuarios.route('/Detalles')
# def detallesListado():
#     return render_template("informacionDocumentada/detalleListado.html")

@usuarios.route('/Detalles/Listado')
def detallesListadoMaes():
    con = get_db_connection()
    cur = con.cursor()
    
    # Ejecutar la consulta y obtener los datos
    cur.execute('SELECT * FROM documentos')
    data = cur.fetchall()  # Devuelve una lista de tuplas con los datos
    
    con.commit()
    cur.close()
    con.close()
    
    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título del documento
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, "Listado de Documentos", ln=True, align="C")
    pdf.ln(10)  # Espacio después del título
    
    # Tabla con los datos
    pdf.set_font("Arial", size=12)
    pdf.cell(40, 10, "Código Documento", border=1, align="C")
    pdf.cell(40, 10, "Número Revisión", border=1, align="C")
    pdf.cell(50, 10, "Fecha Emisión", border=1, align="C")
    pdf.cell(50, 10, "Fecha Revisión", border=1, align="C")
    pdf.ln()  # Salto de línea para la siguiente fila
    
    # Insertar datos en la tabla
    for item in data:
        pdf.cell(40, 10, item[0], border=1)  # Código Documento (ajusta índice según la consulta)
        pdf.cell(40, 10, item[1], border=1)  # Número Revisión
        pdf.cell(50, 10, item[2], border=1)  # Fecha Emisión
        pdf.cell(50, 10, item[3], border=1)  # Fecha Revisión
        pdf.ln()
    
    # Convertir el PDF a un archivo descargable
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=ListadoDocumentos.pdf'
    
    return response
    # return render_template('informacionDocumentada/detalleListado.html')