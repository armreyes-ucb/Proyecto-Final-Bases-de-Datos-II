from flask import Blueprint, redirect, render_template, request, url_for

from database import dbConnection
from models.product import Product


products_bp = Blueprint("products", __name__)
db = dbConnection()
products = db["products"]


@products_bp.route("/")
def home():
    products_received = products.find()
    return render_template("products/index.html", products=products_received)


@products_bp.route("/products", methods=["POST"])
def add_product():
    # Accept the new Spanish field names and keep temporary compatibility
    # with the original tutorial form until the write views are replaced.
    nombre = request.form.get("nombre", request.form.get("name", "")).strip()
    descripcion = request.form.get("descripcion", "").strip()
    precio_text = request.form.get("precio", request.form.get("price", "")).strip()
    stock_text = request.form.get("stock", request.form.get("quantity", "")).strip()
    categoria = request.form.get("categoria", "").strip()
    imagen = request.form.get("imagen", "").strip()

    if not nombre or not precio_text or not stock_text:
        return _not_found()

    try:
        precio = float(precio_text)
        stock = int(stock_text)
    except ValueError:
        return _not_found()

    product = Product(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        categoria=categoria,
        imagen=imagen,
    )
    products.insert_one(product.toDBCollection())
    return redirect(url_for("products.home"))


@products_bp.route("/delete/<string:product_name>")
def delete(product_name):
    products.delete_one({"name": product_name})
    return redirect(url_for("products.home"))


@products_bp.route("/edit/<string:product_name>", methods=["POST"])
def edit(product_name):
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    quantity = request.form.get("quantity", "").strip()

    if name and price and quantity:
        products.update_one(
            {"name": product_name},
            {"$set": {"name": name, "price": price, "quantity": quantity}},
        )
        return redirect(url_for("products.home"))

    return _not_found()


def _not_found():
    return {"message": "Datos incompletos", "status": "404 Not Found"}, 404
