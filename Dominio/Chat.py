from typing import Any, Dict, List
from Menu import menuCompleto  # Asegurate que Menu.py tenga menuCompleto
# from Pedido import Pedido  # Descomentar si tienes la clase Pedido
# from GrafoPedidos import GrafoPedidos  # Descomentar si tienes la clase GrafoPedidos

PAGE_SIZE = 5  # cantidad de productos por página

def get_paginated_menu(page: int = 1, categoria: str = None) -> List[Dict[str, Any]]:
    resultados = menuCompleto

    if categoria:
        resultados = [item for item in resultados if item["categoria"].lower() == categoria.lower()]

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    return resultados[start:end]


class Chat:
    def __init__(self, nombre_restaurante="MiRestaurante"):
        self.pagina_actual = 1
        self.categoria_actual = None
        self.orden_por_precio = None  # 'asc' o 'desc'
        self.carrito: List[Dict[str, Any]] = []
        self.pedidos_tanda: List[Any] = []
        self.nombre_restaurante = nombre_restaurante
        self.grafo_pedidos = None  # Debe ser asignado un objeto con métodos generar_rutas y dijkstra

    # --------------------------
    # MENÚ Y PAGINACIÓN
    # --------------------------
    def generar_mensaje_menu(self) -> Dict[str, Any]:
        productos = get_paginated_menu(self.pagina_actual, self.categoria_actual)

        if self.orden_por_precio == "asc":
            productos.sort(key=lambda x: x["precio"])
        elif self.orden_por_precio == "desc":
            productos.sort(key=lambda x: x["precio"], reverse=True)

        texto = "🍔 *Menú disponible:*\nSeleccioná un producto o una acción.\n"

        rows_acciones = []
        if self.pagina_actual >= 3:
            rows_acciones.append({"id": "go_first_page", "title": "🔁 Volver al inicio"})
        if self.pagina_actual >= 2:
            rows_acciones.append({"id": "prev_page", "title": "⬅️ Página anterior"})
        rows_acciones.append({"id": "next_page", "title": "➡️ Página siguiente"})
        rows_acciones.append({"id": "ordenar", "title": "↕️ Ordenar precio"})
        rows_acciones.append({"id": "filtrar_categoria", "title": "📂 Filtrar por categoría"})

        botones = {
            "type": "list",
            "header": {"type": "text", "text": "Menú de productos"},
            "body": {"text": texto},
            "footer": {"text": f"📄 Página {self.pagina_actual}"},
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Productos disponibles",
                        "rows": [
                            {
                                "id": f"producto_{p['id']}",
                                "title": f"{p['nombre']} - ${p['precio']}",
                                "description": p["descripcion"]
                            } for p in productos
                        ]
                    },
                    {
                        "title": "Acciones",
                        "rows": rows_acciones
                    }
                ]
            }
        }

        return botones

    # --------------------------
    # CARRITO Y POST-SELECCIÓN
    # --------------------------
    def agregar_producto_al_carrito(self, producto: Dict[str, Any]):
        self.carrito.append(producto)

    def generar_mensaje_post_seleccion_producto(self, producto: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "button",
            "body": {"text": f"🛒 *{producto['nombre']}* agregado.\n¿Qué querés hacer ahora?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "seguir_agregando", "title": "➕ Agregar otro"}},
                    {"type": "reply", "reply": {"id": "finalizar_pedido", "title": "✔️ Finalizar pedido"}}
                ]
            }
        }

    def finalizar_pedido_en_grafo(self, cliente: str, ubicacion=(0.0, 0.0)):
        if not self.carrito:
            return "⚠️ No tenés productos en el carrito."

        pedido = Pedido(cliente=cliente, ubicacion=ubicacion, items=self.carrito.copy())
        self.pedidos_tanda.append(pedido)

        if self.grafo_pedidos:
            self.grafo_pedidos.generar_rutas(self.nombre_restaurante, self.pedidos_tanda)
            distancias = self.grafo_pedidos.dijkstra(self.nombre_restaurante)
            distancia_cliente = distancias.get(cliente, None)
        else:
            distancia_cliente =  None 

        self.carrito.clear()

        mensaje = "🧾 *Pedido finalizado*\n"
        if distancia_cliente is not None:
            mensaje += f"📍 Distancia estimada: {distancia_cliente} km\n"
        mensaje += "🎉 Gracias por tu compra 🙌"
        return mensaje

    # --------------------------
    # MANEJO DE ACCIONES
    # --------------------------
    def manejar_accion(self, accion_id: str):
        # Paginación
        if accion_id == "next_page":
            self.pagina_actual += 1
        elif accion_id == "prev_page" and self.pagina_actual > 1:
            self.pagina_actual -= 1
        elif accion_id == "go_first_page":
            self.pagina_actual = 1
            self.categoria_actual = None

        # Ordenamiento
        elif accion_id == "ordenar":
            if self.orden_por_precio == "asc":
                self.orden_por_precio = "desc"
            else:
                self.orden_por_precio = "asc"

         #Mostrar opciones de filtrado (Tu código original, ahora en su lugar)
        elif accion_id.startswith("filtro_"):
            categoria_seleccionada = accion_id.replace("filtro_", "")
            self.categoria_actual = categoria_seleccionada
            self.pagina_actual = 1 ###

        # Filtrado por categoría
        elif accion_id == "filtrar_categoria":
            categorias = sorted(set(item["categoria"] for item in menuCompleto))
            botones_categorias = [
                {"type": "reply", "reply": {"id": f"filtro_{cat.lower()}", "title": f"📁 {cat}"}}
                for cat in categorias
            ]
            return {
                "type": "button",
                "body": {"text": "Seleccioná una categoría para filtrar el menú 👇"},
                "action": {"buttons": botones_categorias}
            }

        # Seguir agregando productos
        elif accion_id == "seguir_agregando":
            return self.generar_mensaje_menu()

        # Finalizar pedido
        elif accion_id == "finalizar_pedido":
            return {
                "type": "text",
                "body": {"text": "🎉 ¡Pedido finalizado! Gracias por tu compra 🙌"}
            }

        # Selección de producto
        elif accion_id.startswith("producto_"):
            producto_id = int(accion_id.replace("producto_", ""))
            producto = next((p for p in menuCompleto if p["id"] == producto_id), None)
            if not producto:
                return {"type": "text", "body": {"text": "❌ Producto no encontrado"}}

            self.agregar_producto_al_carrito(producto)
            return self.generar_mensaje_post_seleccion_producto(producto)

        # Retorna menú actualizado
        return self.generar_mensaje_menu()
