from .utils.utils import get_db_connection, paginador1, allowed_username
from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask
from flask import Flask, request

app = Flask(__name__)

@app.route('/guardar_documento', methods=['POST'])
def guardar_documento():
    # Obtener los datos del formulario
    documentos = request.form.getlist('documentos[0][codigoDocumento]')
    revision = request.form.getlist('documentos[0][numeroRevision]')
    fecha_emision = request.form.getlist('documentos[0][fechaEmision]')
    fecha_revision = request.form.getlist('documentos[0][fechaRevision]')

    # Puedes crear un array de diccionarios para representar todos los documentos
    documentos_data = []
    
    for i in range(len(documentos)):
        documento = {
            'codigoDocumento': documentos[i],
            'numeroRevision': revision[i],
            'fechaEmision': fecha_emision[i],
            'fechaRevision': fecha_revision[i]
        }
        documentos_data.append(documento)

    # Ahora `documentos_data` es un array de diccionarios con los datos de los documentos
    print(documentos_data)  # Solo para comprobar los datos recibidos
    array = request.form['documentos_data']
    
    con = get_db_connection()
    cur = con.cursor()
    sql = "INSERT INTO documentos (array) VALUES %s"
    valores =(array)
    cur.execute(sql,valores)
    con.commit()
    cur.close()
    con.close()
    flash('Usuario agregado correctamente')
    return redirect(url_for('informacionDocumentada.infoDocu'))