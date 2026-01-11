from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime
import config

app = Flask(__name__)
app.config["MONGO_URI"] = config.MONGO_URI
mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template("index.html")

# ================= CATEQUISTA =================

@app.route("/Catequista")
def catequista():
    catequistas = list(mongo.db.Catequista.find())
    return render_template("Catequista.html", catequistas=catequistas)

@app.route("/Catequista/nuevo", methods=["GET","POST"])
def nuevo_catequista():
    if request.method == "POST":
        mongo.db.Catequista.insert_one({
            'nombreCatequista': request.form['nombre'],
            'apellidoCatequista': request.form['apellido'],
            'telefonoCatequista': request.form['telefono'],
            'idParroquia': request.form['idParroquia']
        })
        return redirect(url_for("catequista"))
    return render_template("Catequista_form.html", accion="Nuevo", catequista=None)

@app.route("/Catequista/editar/<id>", methods=["GET","POST"])
def editar_catequista(id):
    if request.method == "POST":
        mongo.db.Catequista.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nombreCatequista': request.form['nombre'],
                'apellidoCatequista': request.form['apellido'],
                'telefonoCatequista': request.form['telefono'],
                'idParroquia': request.form['idParroquia']
            }}
        )
        return redirect(url_for("catequista"))
    catequista = mongo.db.Catequista.find_one({'_id': ObjectId(id)})
    return render_template("Catequista_form.html", accion="Editar", catequista=catequista)

@app.route("/Catequista/eliminar/<id>", methods=["POST"])
def eliminar_catequista(id):
    mongo.db.Catequista.delete_one({'_id': ObjectId(id)})
    return redirect(url_for("catequista"))

# ================= CATEQUIZANDO =================

@app.route("/Catequizando")
def catequizando():
    catequizandos = list(mongo.db.Catequizando.find())
    for c in catequizandos:
        if isinstance(c.get('fechaNacimiento'), datetime):
            c['fechaNacimiento'] = c['fechaNacimiento'].strftime('%Y-%m-%d')

    niveles = {}
    for c in catequizandos:
        nivel = c.get("idNivel", "Sin Nivel")
        niveles[nivel] = niveles.get(nivel, 0) + 1

    return render_template("Catequizando.html", catequizandos=catequizandos, total=len(catequizandos), niveles_resumen=niveles)

@app.route("/Catequizando/nuevo", methods=["GET","POST"])
def nuevo_catequizando():
    if request.method == "POST":
        mongo.db.Catequizando.insert_one({
            'nombreCatequizando': request.form['nombre'],
            'apellidoCatequizando': request.form['apellido'],
            'cedulaCatequizando': request.form['cedula'],
            'fechaNacimiento': datetime.strptime(request.form['fechaNacimiento'], "%Y-%m-%d"),
            'idNivel': request.form['idNivel']
        })
        return redirect(url_for("catequizando"))
    return render_template("Catequizando_form.html", accion="Nuevo", catequizando=None)

@app.route("/Catequizando/editar/<id>", methods=["GET","POST"])
def editar_catequizando(id):
    if request.method == "POST":
        mongo.db.Catequizando.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nombreCatequizando': request.form['nombre'],
                'apellidoCatequizando': request.form['apellido'],
                'cedulaCatequizando': request.form['cedula'],
                'fechaNacimiento': datetime.strptime(request.form['fechaNacimiento'], "%Y-%m-%d"),
                'idNivel': request.form['idNivel']
            }}
        )
        return redirect(url_for("catequizando"))

    catequizando = mongo.db.Catequizando.find_one({'_id': ObjectId(id)})
    if isinstance(catequizando.get("fechaNacimiento"), datetime):
        catequizando["fechaNacimiento"] = catequizando["fechaNacimiento"].strftime("%Y-%m-%d")

    return render_template("Catequizando_form.html", accion="Editar", catequizando=catequizando)

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
                'telefonoSede': request.form['telefono']
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
                    'telefonoSede': request.form['telefono']
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

if __name__ == "__main__":
    app.run(debug=True)
