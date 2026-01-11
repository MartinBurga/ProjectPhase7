from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
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
        # idJoven siempre debe ser ObjectId
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

# ================= CATEQUIZANDO =================
@app.route("/Catequizando")
def catequizando():
    catequizandos = list(mongo.db.Catequizando.find())
    niveles_dict = {str(n['_id']): n['nombreNivel'] for n in mongo.db.Nivel.find()}

    niveles_resumen = {}
    for c in catequizandos:
        if isinstance(c.get('fechaNacimiento'), datetime):
            c['fechaNacimiento'] = c['fechaNacimiento'].strftime('%Y-%m-%d')
        # Convertir ObjectId a string para usar en template
        c['idNivel'] = str(c['idNivel']) if c.get('idNivel') else ''
        c['nombreNivel'] = niveles_dict.get(c.get('idNivel'), "Sin Nivel")

        # Resumen
        nivel = c['nombreNivel']
        niveles_resumen[nivel] = niveles_resumen.get(nivel, 0) + 1

    return render_template(
        "Catequizando.html", 
        catequizandos=catequizandos, 
        total=len(catequizandos), 
        niveles_resumen=niveles_resumen
    )

@app.route("/Catequizando/nuevo", methods=["GET","POST"])
def nuevo_catequizando():
    niveles = list(mongo.db.Nivel.find())
    for n in niveles:
        n['_id'] = str(n['_id'])  # Convertir ObjectId a string

    if request.method == "POST":
        mongo.db.Catequizando.insert_one({
            'nombreCatequizando': request.form['nombre'],
            'apellidoCatequizando': request.form['apellido'],
            'cedulaCatequizando': request.form['cedula'],
            'fechaNacimiento': datetime.strptime(request.form['fechaNacimiento'], "%Y-%m-%d"),
            'idNivel': ObjectId(request.form['idNivel']) if request.form['idNivel'] else None
        })
        return redirect(url_for("catequizando"))

    return render_template("Catequizando_form.html", accion="Nuevo", catequizando=None, niveles=niveles)

@app.route("/Catequizando/editar/<id>", methods=["GET","POST"])
def editar_catequizando(id):
    niveles = list(mongo.db.Nivel.find())
    for n in niveles:
        n['_id'] = str(n['_id'])

    catequizando = mongo.db.Catequizando.find_one({'_id': ObjectId(id)})
    if isinstance(catequizando.get("fechaNacimiento"), datetime):
        catequizando["fechaNacimiento"] = catequizando["fechaNacimiento"].strftime("%Y-%m-%d")
    # Convertir ObjectId a string para seleccionar el nivel en template
    catequizando['idNivel'] = str(catequizando['idNivel']) if catequizando.get('idNivel') else ''

    if request.method == "POST":
        mongo.db.Catequizando.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nombreCatequizando': request.form['nombre'],
                'apellidoCatequizando': request.form['apellido'],
                'cedulaCatequizando': request.form['cedula'],
                'fechaNacimiento': datetime.strptime(request.form['fechaNacimiento'], "%Y-%m-%d"),
                'idNivel': ObjectId(request.form['idNivel']) if request.form['idNivel'] else None
            }}
        )
        return redirect(url_for("catequizando"))

    return render_template("Catequizando_form.html", accion="Editar", catequizando=catequizando, niveles=niveles)

@app.route("/Catequizando/eliminar/<id>", methods=["POST"])
def eliminar_catequizando(id):
    mongo.db.Catequizando.delete_one({'_id': ObjectId(id)})
    return redirect(url_for("catequizando"))

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
