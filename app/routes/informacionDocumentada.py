from flask import Flask, request, redirect, url_for, flash, render_template
from .utils.utils import get_db_connection
import json  # Importar el módulo json
from flask import Blueprint

# Definir el Blueprint
guardar_documentobp = Blueprint('guardar_documento', __name__)

app = Flask(__name__)

@app.route('/informacionDocumentada')
def infoDocu():
    return render_template('informacionDocumentada/index.html')

@app.route('/guardar_documento', methods=['POST'])
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
    
    # Mostrar el JSON en consola para verificar (esto solo para depuración)
    print(documentos_json)
    
    # Insertar los datos en la base de datos
    con = get_db_connection()
    cur = con.cursor()
    
    # Preparamos la consulta para insertar el JSON en la base de datos
    sql = "INSERT INTO documentos (array) VALUES (%s)"
    valores = (documentos_json,)  # El valor debe ser una tupla
    cur.execute(sql, valores)
    
    con.commit()
    cur.close()
    con.close()
    
    flash('Documento guardado correctamente')
    return redirect(url_for('informacionDocumentada.infoDocu'))
