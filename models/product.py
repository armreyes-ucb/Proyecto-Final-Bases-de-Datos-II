class Product:
    def __init__(
        self,
        nombre,
        descripcion,
        precio,
        stock,
        categoria,
        imagen,
    ):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = float(precio)
        self.stock = int(stock)
        self.categoria = categoria
        self.imagen = imagen

    def toDBCollection(self):
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "stock": self.stock,
            "categoria": self.categoria,
            "imagen": self.imagen,
        }

    @staticmethod
    def from_mongo(document):
        return Product(
            document.get("nombre", ""),
            document.get("descripcion", ""),
            document.get("precio", 0),
            document.get("stock", 0),
            document.get("categoria", ""),
            document.get("imagen", ""),
        )

    def get_image(self):
        return self.imagen or "/static/uploads/default.png"
