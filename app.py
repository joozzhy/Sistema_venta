from flask import Flask, render_template, request, redirect, url_for
import json
import os
import datetime
app = Flask(__name__)

# ---------------------------
# FUNCIONES PARA PROMOS
# ---------------------------
PROMOS_FILE = "promociones.json"
CARRITO_FILE = "carrito.json"



# ---------------------------
# FUNCIONES PARA EL CARRITO
# ---------------------------

def cargar_promos():
    with open(PROMOS_FILE, "r") as f:
        return json.load(f)
    
def cargar_carrito():
    if not os.path.exists(CARRITO_FILE):
        return []
    with open(CARRITO_FILE, "r") as f:
        return json.load(f)

def guardar_carrito(carrito):
    with open(CARRITO_FILE, "w") as f:
        json.dump(carrito, f, indent=4)

def guardar_promos(promos):
    with open(PROMOS_FILE, "w") as f:
        json.dump(promos, f, indent=4)


promos = cargar_promos()   # Carga las promos al inicio


# ---------------------------
# RUTA: Formulario principal
# ---------------------------

@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("nueva_promocion.html")



@app.route("/agregar_promocion", methods=["POST"])
def agregar_promocion():
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    precio = int(request.form.get("precio"))

    promociones = cargar_promos()

    nueva_promo = {
        "id": len(promos) + 1,
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio
    }

    promos.append(nueva_promo)
    guardar_promos(promos)

    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html", promos=promos)


# ---------------------------
# RUTA: Detalle de promoción
# ---------------------------
@app.route("/seleccionar", methods=["POST"])
def seleccionar():
    promo_id = int(request.form.get("promo_id"))
    cantidad = int(request.form.get("cantidad"))

    promo = next((p for p in promos if p["id"] == promo_id), None)
    total = promo["precio"] * cantidad

    ahora = datetime.datetime.now()

    return render_template(
        "mostrar.html",
        promo=promo,
        cantidad=cantidad,
        total=total,
        hora_actual=ahora
    )


# ---------------------------
# RUTA: Agregar al carrito
# ---------------------------
@app.route("/agregar", methods=["POST"])
def agregar():
    promo_id = int(request.form.get("promo_id"))
    cantidad = int(request.form.get("cantidad"))

    promo = next((p for p in promos if p["id"] == promo_id), None)

    item = {
        "promo_id": promo["id"],
        "nombre": promo["nombre"],
        "precio_unit": promo["precio"],
        "cantidad": cantidad,
        "fecha" : datetime.datetime.now().strftime('%d-%m-%Y %H:%M'),
        "total": promo["precio"] * cantidad
    }

    carrito = cargar_carrito()
    carrito.append(item)
    guardar_carrito(carrito)

    return redirect(url_for("ver_carrito"))


# ---------------------------
# RUTA: Ver carrito
# ---------------------------
@app.route("/carrito")
def ver_carrito():
    carrito = cargar_carrito()
    total_general = sum(item["total"] for item in carrito)

    

    return render_template(
        "carrito.html",
        carrito=carrito,
        total_general=total_general,
        
    )


# ---------------------------
# RUTA: Eliminar item del carrito
# ---------------------------
@app.route("/eliminar/<int:index>")
def eliminar(index):
    carrito = cargar_carrito()

    if 0 <= index < len(carrito):
        carrito.pop(index)

    guardar_carrito(carrito)
    return redirect(url_for("ver_carrito"))




@app.route("/editar/<int:index>")
def editar_item(index):
    carrito = cargar_carrito()
    if 0 <= index < len(carrito):
        item = carrito[index]
        return render_template("editar.html", index=index, item=item)
    return redirect(url_for("ver_carrito"))

@app.route("/actualizar/<int:index>", methods=["POST"])
def actualizar_item(index):
    carrito = cargar_carrito()
    if 0 <= index < len(carrito):
        cantidad = int(request.form.get("cantidad"))
        carrito[index]["cantidad"] = cantidad
        carrito[index]["total"] = carrito[index]["precio_unit"] * cantidad
        guardar_carrito(carrito)
    return redirect(url_for("ver_carrito"))


if __name__ == "__main__":
    app.run(debug=True)
