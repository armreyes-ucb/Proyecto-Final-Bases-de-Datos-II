import re

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, abort, redirect, render_template, request, url_for

from database import dbConnection
from models.product import Product


products_bp = Blueprint("products", __name__)
db = dbConnection()
products = db["products"]


@products_bp.route("/")
def home():
    products_received = products.find()
    return render_template("products/index.html", products=products_received)


@products_bp.route("/products")
def list_products():
    """List products sorted by name, with optional combined filters."""
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()

    query = {}
    if q:
        query["nombre"] = {"$regex": re.escape(q), "$options": "i"}
    if category:
        query["categoria"] = category

    price_filter = {}
    if min_price:
        try:
            price_filter["$gte"] = float(min_price)
        except ValueError:
            pass
    if max_price:
        try:
            price_filter["$lte"] = float(max_price)
        except ValueError:
            pass
    if price_filter:
        query["precio"] = price_filter

    products_received = list(products.find(query).sort("nombre", 1))
    categories = sorted(
        (value for value in products.distinct("categoria") if value),
        key=lambda value: str(value).lower(),
    )

    return render_template(
        "products/list.html",
        products=products_received,
        categories=categories,
        q=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
    )


@products_bp.route("/products/<string:product_id>")
def product_detail(product_id):
    """Show a single product on its own page."""
    try:
        object_id = ObjectId(product_id)
    except (InvalidId, TypeError):
        abort(404)

    product = products.find_one({"_id": object_id})
    if product is None:
        abort(404)

    return render_template("products/detail.html", product=product)


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
