# Dominio/Chat.py
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass
from Menu import menuCompleto
from Bot.grafo import GrafoPedidos


PAGE_SIZE = 5


@dataclass
class Pedido:
    cliente: str
    ubicacion: Tuple[float, float]
    items: List[Dict[str, Any]]


def get_paginated_menu(page: int = 1, categoria: str = None) -> List[Dict[str, Any]]:
    resultados = menuCompleto

    if categoria:
        resultados = [
            item for item in resultados
            if item["categoria"].lower() == categoria.lower()
        ]

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    return resultados[start:end]


class Chat:
    def __init__(self, nombre_restaurante: str = "Restaurante"):
        self.pagina_Actual = 1
        self.categoria_Actual = None
        self.orden_por_precio = None

        self.carrito: List[Dict[str, Any]] = []

        self.nombre_restaurante = nombre_restaurante
        self.grafo_pedidos = GrafoPedidos()
        self.pedidos_tanda: List[Pedido] = []

    # --------------------------
    # MENÚ PRINCIPAL
    # --------------------------
    def generar_mensaje_menu(self) -> Dict[str, Any]:
        productos = get_paginated_menu(self.pagina_Actual, self.categoria_Actual)

        if self.orden_por_precio == "asc":
            productos.sort(key=lambda x: x["precio"])
        elif self.orden_por_precio == "desc":
            productos.sort(key=lambda x: x["precio"], reverse=True)

        botones = {
            "type": "list",
            "header": {"type": "text", "text": "Menú de productos"},
            "body": {"text": "🍔 *Menú disponible:* Seleccioná un producto."},
            "footer": {"text": f"📄 Página {self.pagina_Actual}"},
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Productos",
                        "rows": [
                            {
                                "id": f"producto_{p['id']}",
                                "title": f"{p['nombre']} - ${p['precio']}",
                                "description": p["descripcion"],
                            }
                            for p in productos
                        ],
                    },
                    {
                        "title": "Acciones",
                        "rows": [],
                    },
                ],
            },
        }

        rows = []

        if self.pagina_Actual >= 2:
            rows.append({"id": "go_first_page", "title": "🔁 Volver al inicio"})
            rows.append({"id": "prev_page", "title": "⬅️ Página anterior"})

        rows.append({"id": "next_page", "title": "➡️ Página siguiente"})
        rows.append({"id": "ordenar", "title": "↕️ Ordenar precio"})
        rows.append({"id": "filtrar_categoria", "title": "📂 Filtrar por categoría"})

        botones["action"]["sections"][1]["rows"] = rows
        return botones

    # --------------------------
    # CARRITO Y POST-SELECCIÓN
    # --------------------------
    def agregar_producto_al_carrito(self, producto):
        self.carrito.append(producto)

    def generar_mensaje_post_seleccion_producto(self, producto):
        return {
            "type": "button",
            "body": {
                "text": f"🛒 *{producto['nombre']}* agregado.\n¿Qué querés hacer ahora?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "seguir_agregando", "title": "➕ Agregar otro"},
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "finalizar_pedido", "title": "✔️ Finalizar pedido"},
                    },
                ]
            },
        }

    def finalizar_pedido_en_grafo(self, cliente, ubicacion):
        if not self.carrito:
            return "⚠️ No tenés productos en el carrito."

        pedido = Pedido(cliente=cliente, ubicacion=ubicacion, items=self.carrito.copy())
        self.pedidos_tanda.append(pedido)

        self.grafo_pedidos.generar_rutas(self.nombre_restaurante, self.pedidos_tanda)

        distancias = self.grafo_pedidos.dijkstra(self.nombre_restaurante)
        distancia_cliente = distancias.get(cliente, None)

        self.carrito.clear()

        mensaje = "🧾 *Pedido finalizado*\n"

        if distancia_cliente is not None:
            mensaje += f"📍 Distancia estimada: {distancia_cliente} km\n"

        mensaje += "🎉 Gracias por tu compra 🙌"

        return mensaje

    # --------------------------
    # MANEJO DE ACCIONES
    # --------------------------
    def manejar_accion(self, accion_id: str, cliente: str, ubicacion=(0.0, 0.0)):
        if accion_id == "next_page":
            self.pagina_Actual += 1

        elif accion_id == "prev_page" and self.pagina_Actual > 1:
            self.pagina_Actual -= 1

        elif accion_id == "ordenar":
            self.orden_por_precio = "asc" if self.orden_por_precio != "asc" else "desc"

        elif accion_id == "go_first_page":
            self.pagina_Actual = 1

        elif accion_id == "seguir_agregando":
            return self.generar_mensaje_menu()

        elif accion_id == "finalizar_pedido":
            texto = self.finalizar_pedido_en_grafo(cliente, ubicacion)
            return {"type": "text", "body": {"text": texto}}

        elif accion_id.startswith("producto_"):
            producto_id = int(accion_id.replace("producto_", ""))
            producto = next((p for p in menuCompleto if p["id"] == producto_id), None)

            if not producto:
                return {"type": "text", "body": {"text": "❌ Producto no encontrado"}}

            self.agregar_producto_al_carrito(producto)
            return self.generar_mensaje_post_seleccion_producto(producto)

        return self.generar_mensaje_menu()
