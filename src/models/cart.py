class ShoppingCart:
    def __init__(self):
        self.items = []

    def __add__(self, item):
        """Добавление товара через оператор +"""
        new_cart = ShoppingCart()
        new_cart.items = self.items.copy()
        new_cart.items.append(item)
        return new_cart

    def __len__(self):
        """Количество товаров в корзине"""
        return len(self.items)

    def __iter__(self):
        """Итерация по товарам"""
        return iter(self.items)

    def __str__(self):
        return f"Корзина: {len(self.items)} товаров"
