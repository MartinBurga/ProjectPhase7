from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime
from datetime import datetime
import config

app = Flask(__name__)
app.config["MONGO_URI"] = config.MONGO_URI
mongo = PyMongo(app)

# ================= INDEX =================
@app.route("/")
def index():
    return render_template("index.html")

# ================= CATEQUISTA =================
@app.route("/Catequista")
def catequista():
    catequistas = list(mongo.db.Catequista.find())

    parroquias = list(mongo.db.Parroquia.find())
    parroquias_dict = {str(p['_id']): p['nombre'] for p in parroquias}

    for c in catequistas:
        id_parroquia = str(c.get('idParroquia')) if c.get('idParroquia') else None
        c['nombreParroquia'] = parroquias_dict.get(id_parroquia, "Sin Parroquia")

        if 'jovenApoyo' not in c or not c['jovenApoyo']:
            c['jovenApoyo'] = {'nombresJoven':'', 'cedulaJoven':''}

    return render_template("Catequista.html", catequistas=catequistas)



@app.route("/Catequista/nuevo", methods=["GET","POST"])
def nuevo_catequista():
    if request.method == "POST":
        mongo.db.Catequista.insert_one({
            'nombreCatequista': request.form['nombre'],
            'apellidoCatequista': request.form['apellido'],
            'cedula': request.form['cedula'],
            'telefonoCatequista': request.form['telefono'],
            'idParroquia': request.form['idParroquia'],
            'jovenApoyo': {
                'nombresJoven': request.form['Joven Apoyo'],
                'cedulaJoven': request.form['Cedula Joven']
            }
        })
        return redirect(url_for("catequista"))

    parroquias = list(mongo.db.Parroquia.find())
    for p in parroquias:
        p['_id'] = str(p['_id'])

    return render_template("Catequista_form.html", accion="Nuevo", catequista=None, parroquias=parroquias)

@app.route("/Catequista/editar/<id>", methods=["GET","POST"])
def editar_catequista(id):
    catequista = mongo.db.Catequista.find_one({'_id': ObjectId(id)})

    parroquias = list(mongo.db.Parroquia.find())
    for p in parroquias:
        p['_id'] = str(p['_id'])

    if request.method == "POST":
        if 'jovenApoyo' in catequista and 'idJoven' in catequista['jovenApoyo']:
            id_joven = catequista['jovenApoyo']['idJoven']
        else:
            id_joven = ObjectId()

        mongo.db.Catequista.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nombreCatequista': request.form['nombre'],
                'apellidoCatequista': request.form['apellido'],
                'cedula': request.form['cedula'],
                'telefonoCatequista': request.form['telefono'],
                'idParroquia': request.form['idParroquia'] if request.form.get('idParroquia') else "",
                'jovenApoyo': {
                    'idJoven': ObjectId(id_joven),
                    'nombresJoven': request.form['Joven Apoyo'],
                    'cedulaJoven': request.form['Cedula Joven']
                }
            }}
        )
        return redirect(url_for("catequista"))

    return render_template(
        "Catequista_form.html",
        accion="Editar",
        catequista=catequista,
        parroquias=parroquias
    )

@app.route("/Catequista/eliminar/<id>", methods=["POST"])
def eliminar_catequista(id):
    mongo.db.Catequista.delete_one({'_id': ObjectId(id)})
    return redirect(url_for("catequista"))

# ---------------- Listado resumido ----------------
@app.route("/Catequizando")
def catequizando():
    catequizandos = list(mongo.db.Catequizando.find())

    # Traer todos los niveles
    niveles = {str(n['_id']): n['nombreNivel'] for n in mongo.db.Nivel.find()}

    niveles_resumen = {}

    for c in catequizandos:
        # Formatear fecha de nacimiento
        if isinstance(c.get('fechaNacimiento'), datetime):
            c['fechaNacimientoStr'] = c['fechaNacimiento'].strftime('%Y-%m-%d')
        else:
            c['fechaNacimientoStr'] = ''

        nivel_id = str(c.get('idNivel', 'Sin Nivel'))
        c['nombreNivel'] = niveles.get(nivel_id, 'Sin Nivel')

        c['nombreRepresentante'] = c.get('representante', {}).get('nombreRepresentante', 'Sin Representante')

        niveles_resumen[c['nombreNivel']] = niveles_resumen.get(c['nombreNivel'], 0) + 1

    return render_template(
        "Catequizando.html",
        catequizandos=catequizandos,
        total=len(catequizandos),
        niveles_resumen=niveles_resumen
    )

# ---------------- Detalle completo ----------------
@app.route("/Catequizando/detalle/<id>")
def detalle_catequizando(id):
    c = mongo.db.Catequizando.find_one({'_id': ObjectId(id)})
    # Historial de faltas
    faltas = []

    if c.get("inasistencias"):
        for f in c["inasistencias"]:
            fecha = f["fecha"].strftime("%Y-%m-%d") if isinstance(f["fecha"], datetime) else f["fecha"]
            faltas.append({
                "fecha": fecha,
                "presente": f["presente"]
            })
    # ---------- Formatear fechas ----------
    if isinstance(c.get('fechaNacimiento'), datetime):
        c['fechaNacimientoStr'] = c['fechaNacimiento'].strftime('%Y-%m-%d')

    if c.get('inscripcion') and isinstance(c['inscripcion'].get('fechaInscripcion'), datetime):
        c['inscripcion']['fechaInscripcionStr'] = c['inscripcion']['fechaInscripcion'].strftime('%Y-%m-%d')

    if c.get('inasistencia') and isinstance(c['inasistencia'].get('fechaInasistencia'), datetime):
        c['inasistencia']['fechaInasistenciaStr'] = c['inasistencia']['fechaInasistencia'].strftime('%Y-%m-%d')

    # ---------- Nivel y Certificado ----------
    nivel = None
    certificado = None

    if c.get('idNivel'):
        nivel = mongo.db.Nivel.find_one({'_id': ObjectId(c['idNivel'])})
        if nivel:
            c['nombreNivel'] = nivel.get('nombreNivel', 'Sin Nivel')
            certificado = nivel.get('certificado')
        else:
            c['nombreNivel'] = 'Sin Nivel'
    else:
        c['nombreNivel'] = 'Sin Nivel'

    return render_template(
        "Catequizando_detalle.html",
        catequizando=c,
        nivel=nivel,
        certificado=certificado,
        faltas=faltas
    )


# ---------------- Editar catequizando ----------------
@app.route("/Catequizando/editar/<id>", methods=["GET","POST"])
def editar_catequizando(id):
    catequizando = mongo.db.Catequizando.find_one({'_id': ObjectId(id)})
    niveles = list(mongo.db.Nivel.find())

    # Convertir ObjectId a string para el select
    for n in niveles:
        n['_id'] = str(n['_id'])

    if request.method == "POST":
        mongo.db.Catequizando.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                # Información personal
                'nombreCatequizando': request.form['nombre'],
                'apellidoCatequizando': request.form['apellido'],
                'cedulaCatequizando': request.form['cedula'],
                'fechaNacimiento': datetime.strptime(request.form['fechaNacimiento'], "%Y-%m-%d"),
                'tipoSangre': request.form['tipoSangre'],
                'lugarResidencia': request.form['lugarResidencia'],
                'lugarNacimiento': request.form['lugarNacimiento'],
                'idNivel': ObjectId(request.form['idNivel']) if request.form['idNivel'] else None,

                # Representante
                'representante': {
                    'nombreRepresentante': request.form['nombreRepresentante'],
                    'apellidoRepresentante': request.form['apellidoRepresentante'],
                    'numeroRepresentante': request.form['numeroRepresentante'],
                    'tipoRepresentante': request.form['tipoRepresentante'],
                    'ocupacionRepresentante': request.form['ocupacionRepresentante']
                },

                # Padrino
                'padrino': {
                    'nombresPadrino': request.form['nombresPadrino'],
                    'cedulaPadrino': request.form['cedulaPadrino']
                },

                # Inscripción
                'inscripcion': {
                    'fechaInscripcion': datetime.strptime(request.form['fechaInscripcion'], "%Y-%m-%d"),
                    'estadoInscripcion': True if request.form.get('estadoInscripcion') == 'on' else False
                },

                # Última inasistencia
                'inasistencia': {
                    'fechaInasistencia': datetime.strptime(request.form['fechaInasistencia'], "%Y-%m-%d") if request.form['fechaInasistencia'] else None,
                    'presente': True if request.form.get('presente') == 'on' else False
                }
            }}
        )
        return redirect(url_for("catequizando"))

    # Formatear fechas para mostrar en el form
    if catequizando.get('fechaNacimiento'):
        catequizando['fechaNacimientoStr'] = catequizando['fechaNacimiento'].strftime("%Y-%m-%d")
    if catequizando.get('inscripcion') and catequizando['inscripcion'].get('fechaInscripcion'):
        catequizando['inscripcion']['fechaInscripcionStr'] = catequizando['inscripcion']['fechaInscripcion'].strftime("%Y-%m-%d")
    if catequizando.get('inasistencia') and catequizando['inasistencia'].get('fechaInasistencia'):
        catequizando['inasistencia']['fechaInasistenciaStr'] = catequizando['inasistencia']['fechaInasistencia'].strftime("%Y-%m-%d")

    return render_template("Catequizando_form.html", catequizando=catequizando, niveles=niveles, accion="Editar")

@app.route("/Catequizando/nuevo", methods=["GET","POST"])
def nuevo_catequizando():
    niveles = list(mongo.db.Nivel.find())
    for n in niveles:
        n['_id'] = str(n['_id'])

    if request.method == "POST":
        mongo.db.Catequizando.insert_one({
            'nombreCatequizando': request.form['nombre'],
            'apellidoCatequizando': request.form['apellido'],
            'cedulaCatequizando': request.form['cedula'],
            'fechaNacimiento': datetime.strptime(request.form['fechaNacimiento'], "%Y-%m-%d"),
            'tipoSangre': request.form['tipoSangre'],
            'lugarResidencia': request.form['lugarResidencia'],
            'lugarNacimiento': request.form['lugarNacimiento'],
            'idNivel': ObjectId(request.form['idNivel']) if request.form['idNivel'] else None,
            'representante': {},
            'padrino': {},
            'inscripcion': {},
            'inasistencia': {}
        })
        return redirect(url_for("catequizando"))

    # Inicializar campos vacíos para el form
    catequizando = {
        'nombreCatequizando': '',
        'apellidoCatequizando': '',
        'cedulaCatequizando': '',
        'fechaNacimientoStr': '',
        'tipoSangre': '',
        'lugarResidencia': '',
        'lugarNacimiento': '',
        'idNivel': '',
        'representante': {},
        'padrino': {},
        'inscripcion': {},
        'inasistencia': {}
    }

    return render_template("Catequizando_form.html", catequizando=catequizando, niveles=niveles, accion="Nuevo")



@app.route("/Catequizando/eliminar/<id>", methods=["POST"])
def eliminar_catequizando(id):
    mongo.db.Catequizando.delete_one({'_id': ObjectId(id)})
    return redirect(url_for("catequizando"))



@app.route("/Catequizando/falta/<id>", methods=["POST"])
def registrar_falta(id):
    fecha = request.form.get("fecha")

    mongo.db.Catequizando.update_one(
        {"_id": ObjectId(id)},
        {
            "$push": {
                "inasistencias": {
                    "fecha": datetime.strptime(fecha, "%Y-%m-%d"),
                    "presente": False
                }
            }
        }
    )

    return redirect(url_for("detalle_catequizando", id=id))

# ---------------- Eliminar falta ----------------
@app.route("/Catequizando/eliminar_falta/<id>", methods=["POST"])
def eliminar_falta(id):
    fecha_str = request.form.get("fecha")

    # Convertir a rango de día (00:00:00 → 23:59:59)
    fecha_inicio = datetime.strptime(fecha_str, "%Y-%m-%d")
    fecha_fin = fecha_inicio.replace(hour=23, minute=59, second=59)

    mongo.db.Catequizando.update_one(
        {"_id": ObjectId(id)},
        {
            "$pull": {
                "inasistencias": {
                    "fecha": {
                        "$gte": fecha_inicio,
                        "$lte": fecha_fin
                    }
                }
            }
        }
    )

    return redirect(url_for("detalle_catequizando", id=id))


# ================= PARROQUIA =================
@app.route("/Parroquia")
def parroquia():
    parroquias = list(mongo.db.Parroquia.find())
    return render_template("Parroquia.html", parroquias=parroquias)

@app.route("/Parroquia/nueva", methods=["GET","POST"])
def nueva_parroquia():
    if request.method == "POST":
        mongo.db.Parroquia.insert_one({
            'nombre': request.form['nombre'],
            'sede': {
                'nombreSede': request.form['nombreSede'],
                'direccion': request.form['direccion'],
                'telefonoSede': request.form['telefono'],
                'parroco': request.form['parroco']
            }
        })
        return redirect(url_for("parroquia"))
    return render_template("Parroquia_form.html", accion="Nueva", parroquia=None)

@app.route("/Parroquia/editar/<id>", methods=["GET","POST"])
def editar_parroquia(id):
    if request.method == "POST":
        mongo.db.Parroquia.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nombre': request.form['nombre'],
                'sede': {
                    'nombreSede': request.form['nombreSede'],
                    'direccion': request.form['direccion'],
                    'telefonoSede': request.form['telefono'],
                    'parroco': request.form['parroco'] 
                }
            }}
        )
        return redirect(url_for("parroquia"))

    parroquia = mongo.db.Parroquia.find_one({'_id': ObjectId(id)})
    return render_template("Parroquia_form.html", accion="Editar", parroquia=parroquia)


@app.route("/Parroquia/eliminar/<id>", methods=["POST"])
def eliminar_parroquia(id):
    mongo.db.Parroquia.delete_one({'_id': ObjectId(id)})
    return redirect(url_for("parroquia"))

# ================= NIVELES (SOLO LECTURA) =================
@app.route("/Nivel")
def nivel():
    niveles = list(mongo.db.Nivel.find())
    total = len(niveles)

    for n in niveles:
        n['_id'] = str(n['_id'])
        if 'certificado' in n and n['certificado']:
            n['certificado']['fechaCertificado'] = str(n['certificado']['fechaCertificado'])[:10]
        if 'sacramento' in n and n['sacramento']:
            n['sacramento']['fechaSacramento'] = str(n['sacramento']['fechaSacramento'])[:10]

    return render_template("Nivel.html", niveles=niveles, total=total)

if __name__ == "__main__":
    app.run(debug=True)
