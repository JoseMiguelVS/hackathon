from flask import Flask, request, redirect, url_for, flash
from .utils.utils import get_db_connection

app = Flask(__name__)

@app.route('/guardar_documento', methods=['POST'])
def guardar_documento():
    # Obtener los datos del formulario. Cada campo está dentro de un array debido al índice
    documentos = request.form.getlist('documentos[0][codigoDocumento]')
    revision = request.form.getlist('documentos[0][numeroRevision]')
    fecha_emision = request.form.getlist('documentos[0][fechaEmision]')
    fecha_revision = request.form.getlist('documentos[0][fechaRevision]')
    
    # Crear un array de diccionarios
    documentos_data = []
    
    # Aquí estamos asumiendo que los campos se envían como listas y tienen la misma longitud
    for i in range(len(documentos)):
        documento = {
            'codigoDocumento': documentos[i],
            'numeroRevision': revision[i],
            'fechaEmision': fecha_emision[i],
            'fechaRevision': fecha_revision[i]
        }
        documentos_data.append(documento)
    
    # Mostrar los datos en consola (esto solo para verificar)
    print(documentos_data)
    
    # Insertar los datos en la base de datos
    con = get_db_connection()
    cur = con.cursor()
    
    # Preparamos una consulta para insertar múltiples registros
    for doc in documentos_data:
        sql = "INSERT INTO documentos (codigo_documento, numero_revision, fecha_emision, fecha_revision) VALUES (%s, %s, %s, %s)"
        valores = (doc['codigoDocumento'], doc['numeroRevision'], doc['fechaEmision'], doc['fechaRevision'])
        cur.execute(sql, valores)
    
    con.commit()
    cur.close()
    con.close()
    
    flash('Documento guardado correctamente')
    return redirect(url_for('informacionDocumentada.infoDocu'))
