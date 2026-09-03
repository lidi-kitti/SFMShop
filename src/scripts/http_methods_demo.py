# Создай отдельный файл scripts/http_methods_demo.py
from http import HTTPStatus


class ProductAPI:
    """Мини-роутер SFMShop: хранит товары в памяти и отвечает
    правильным HTTP-методом и статусом, как настоящий REST API."""

    def __init__(self):
        self._products = {}   # id -> {"name": str, "price": float}
        self._next_id = 1

    def handle(self, method, product_id=None, body=None):
        """Возвращает кортеж (status_code, payload)."""
        if method == "GET":
            if product_id is None:
                return HTTPStatus.OK, list(self._products.values())
            elif product_id in self._products:
                return HTTPStatus.OK, self._products[product_id]
            else:
                return HTTPStatus.NOT_FOUND, {"error": "Product not found"}
        elif method == "POST":
            if body is None:
                return HTTPStatus.BAD_REQUEST, {"error": "Body is required"}
            self._products[self._next_id] = body
            self._next_id += 1
            return HTTPStatus.CREATED, body
        elif method == "PUT":
            if product_id is None or body is None:
                return HTTPStatus.BAD_REQUEST, {"error": "Product ID and body are required"}
            if product_id not in self._products:
                return HTTPStatus.NOT_FOUND, {"error": "Product not found"}
            self._products[product_id] = body
            return HTTPStatus.OK, body
        elif method == "DELETE":
            if product_id is None:
                return HTTPStatus.BAD_REQUEST, {"error": "Product ID is required"}
            if product_id not in self._products:
                return HTTPStatus.NOT_FOUND, {"error": "Product not found"}
            del self._products[product_id]
            return HTTPStatus.NO_CONTENT, None
        else:
            return HTTPStatus.METHOD_NOT_ALLOWED, {"error": "Method not allowed"}

def show(label, result):
    status, payload = result
    print(f"{label}: {status.value} {status.phrase} -> {payload}")


api = ProductAPI()
show("GET", api.handle("GET"))
show("GET", api.handle("GET", 1))
show("POST", api.handle("POST", body={"name": "Product 1", "price": 100}))
show("PUT", api.handle("PUT", 1, body={"name": "Product 1", "price": 100}))
show("DELETE", api.handle("DELETE", 1))
show("GET", api.handle("GET"))
show("GET", api.handle("GET", 1))
show("POST", api.handle("POST", body={"name": "Product 1", "price": 100}))
show("PUT", api.handle("PUT", 1, body={"name": "Product 1", "price": 100}))
show("DELETE", api.handle("DELETE", 1))