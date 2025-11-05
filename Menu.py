from typing import Any, Dict, List

menu_categorias: List[Dict[str, str]] = [
    {"id": "Todos", "title": "🧭 Todos"},
    {"id": "Hamburguesas", "title": "🍔 Hamburguesas"},
    {"id": "Pizzas", "title": "🍕 Pizzas"},
    {"id": "Ensaladas", "title": "🥗 Ensaladas"},
    {"id": "Bebidas", "title": "🥤 Bebidas"},
    {"id": "Minutas", "title": "🥪 Minutas"},
    {"id": "Postres", "title": "🍰 Postres"},
]

menu_items: Dict[str, List[Dict[str, Any]]] = {
    "Hamburguesas": [
        {"id": "1",  "title": "Doble chesse",       "price": 320, "category": "Hamburguesas", "description": "Pan de papa, doble carne, cheddar, cebolla y ketchup"},
        {"id": "2",  "title": "Chillout",           "price": 390, "category": "Hamburguesas", "description": "Doble carne, cheddar, panceta, cebolla caramelizada y barbacoa"},
        {"id": "3",  "title": "Bunker",             "price": 450, "category": "Hamburguesas", "description": "Triple carne, cheddar, panceta, huevo, aros, mil islas"},
        {"id": "4",  "title": "Clásica",            "price": 300, "category": "Hamburguesas", "description": "Doble carne, cheddar, tomate, lechuga, mayonesa y ketchup"},
        {"id": "5",  "title": "Hamburguesa Vegana", "price": 330, "category": "Hamburguesas", "description": "Base de lentejas y vegetales frescos"},
    ],
    "Pizzas": [
        {"id": "6",  "title": "Pizza Napolitana", "price": 430, "category": "Pizzas", "description": "Tomate, mozzarella y albahaca"},
        {"id": "7",  "title": "Cuatro Quesos",    "price": 520, "category": "Pizzas", "description": "Mozzarella, parmesano, roquefort y provolone"},
        {"id": "8",  "title": "Pizza Pesto",      "price": 480, "category": "Pizzas", "description": "Mozzarella, pesto, provolone"},
        {"id": "9",  "title": "Pizza Americana",  "price": 500, "category": "Pizzas", "description": "Mozzarella, papas y huevo frito"},
        {"id": "10", "title": "Fugazzeta",        "price": 470, "category": "Pizzas", "description": "Mozzarella, cebolla en julianas, oliva"},
    ],
    "Ensaladas": [
        {"id": "11", "title": "César",        "price": 360, "category": "Ensaladas", "description": "Lechuga, pollo grillado, parmesano y crutones"},
        {"id": "12", "title": "Mediterránea", "price": 340, "category": "Ensaladas", "description": "Mix de verdes, aceitunas, cherry y feta"},
        {"id": "16", "title": "Quinoa Power", "price": 380, "category": "Ensaladas", "description": "Quinoa, kale, garbanzos, zanahoria, limón"},
        {"id": "17", "title": "Caprese",      "price": 320, "category": "Ensaladas", "description": "Tomate, mozzarella, albahaca, oliva"},
    ],
    "Bebidas": [
        {"id": "13", "title": "Coca Cola 350ml", "price": 110, "category": "Bebidas", "description": "Lata 350 ml"},
        {"id": "14", "title": "Fanta 350ml",     "price": 110, "category": "Bebidas", "description": "Lata 350 ml"},
        {"id": "15", "title": "Agua 500ml",      "price": 100, "category": "Bebidas", "description": "Botella 500 ml"},
        {"id": "18", "title": "Sprite 350ml",    "price": 110, "category": "Bebidas", "description": "Lata 350 ml"},
        {"id": "19", "title": "Pomelo 1L",       "price": 180, "category": "Bebidas", "description": "Botella 1 litro"},
    ],
    "Minutas": [
        {"id": "20", "title": "Milanesa al pan", "price": 300, "category": "Minutas", "description": "Lechuga, tomate, mayo"},
        {"id": "21", "title": "Chivito clásico", "price": 520, "category": "Minutas", "description": "Lomo, jamón, queso, lechuga, tomate, huevo"},
        {"id": "22", "title": "Lomito",          "price": 480, "category": "Minutas", "description": "Lomo, queso, cebolla, morrón"},
        {"id": "23", "title": "Panchos x2",      "price": 220, "category": "Minutas", "description": "Pan artesanal, salsas"},
    ],
    "Postres": [
        {"id": "24", "title": "Flan casero",   "price": 190, "category": "Postres", "description": "Con dulce de leche"},
        {"id": "25", "title": "Brownie",       "price": 230, "category": "Postres", "description": "Chocolate intenso"},
        {"id": "26", "title": "Helado 1 bocha","price": 160, "category": "Postres", "description": "Vainilla/Chocolate/Frutilla"},
        {"id": "27", "title": "Chocotorta",    "price": 220, "category": "Postres", "description": "Clásica cremosa"},
        {"id": "28", "title": "Tiramisú",      "price": 250, "category": "Postres", "description": "Estilo italiano"},
    ],
}


ALL_ITEMS: List[Dict[str, Any]] = [p for grupo in menu_items.values() for p in grupo]