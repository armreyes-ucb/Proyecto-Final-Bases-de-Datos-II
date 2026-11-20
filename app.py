from flask import Flask

from models.product import Product
from routes import products_bp


app = Flask(__name__)
app.jinja_env.globals["get_image"] = Product.get_image
app.register_blueprint(products_bp)


@app.errorhandler(404)
def not_found(error=None):
    return {
        "message": "No encontrado " + getattr(error, "description", ""),
        "status": "404 Not Found",
    }, 404


if __name__ == "__main__":
    app.run(debug=True, port=4000)
