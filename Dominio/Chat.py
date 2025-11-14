from typing import Any, Dict, List
from Menu import menuCompleto

PAGE_SIZE = 5  # cantidad de productos por página

def get_paginated_menu(page: int = 1, categoria: str = None) -> List[Dict[str, Any]]:
    resultados = menuCompleto

    # Filtrar por categoría si se pasa
    if categoria:
        resultados = [item for item in resultados if item["categoria"].lower() == categoria.lower()]

    # Paginación
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    paginated = resultados[start:end]

    return paginated  #ddd


class Chat:
    def __init__(self):
        self.pagina_Actual = 1
        self.categoria_Actual = None  # sin filtro por defecto
        self.orden_por_precio = None  # puede ser 'asc' o 'desc'

    def generar_mensaje_menu(self) -> Dict[str, Any]:
        productos = get_paginated_menu(self.pagina_Actual, self.categoria_Actual)

        # Ordenar por precio si corresponde
        if self.orden_por_precio == "asc":
            productos.sort(key=lambda x: x["precio"])
        elif self.orden_por_precio == "desc":
            productos.sort(key=lambda x: x["precio"], reverse=True)

        # Texto principal del cuerpo
        texto = "🍔 *Menú disponible:*\nSeleccioná un producto o una acción.\n"

        # Construcción del mensaje tipo lista
        botones = {
            "type": "list",
            "header": {"type": "text", "text": "Menú de productos"},
            "body": {"text": texto},
            "footer": {"text": f"📄 Página {self.pagina_Actual}"},
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Productos disponibles",
                        "rows": [
                            {
                                "id": f"producto_{p['id']}",
                                "title": f"{p['nombre']} - ${p['precio']}",
                                "description": f"{p['descripcion']}"
                            }
                            for p in productos
                        ]
                    },
                    {
                        "title": "Acciones",
                        "rows": []                        
                    }
                ]
            }
        }
        rows = []

        # Volver al inicio (solo desde página 3)
        if self.pagina_Actual >= 2:
            rows.append({"id": "go_first_page", "title": "🔁 Volver al inicio"})

        # Página anterior (solo desde página 2)
        if self.pagina_Actual >= 2:
            rows.append({"id": "prev_page", "title": "⬅️ Página anterior"})

        # Página siguiente (siempre)
        rows.append({"id": "next_page", "title": "➡️ Página siguiente"})

        # Botones fijos
        rows.append({"id": "ordenar", "title": "↕️ Ordenar precio"})
        rows.append({"id": "filtrar_categoria", "title": "📂 Filtrar por categoría"})

        # Aplicar los nuevos botones a la sección Acciones
        botones["action"]["sections"][1]["rows"] = rows
        return botones

    def manejar_accion(self, accion_id: str, category: str = None):
        # Acciones del usuario
        if accion_id == "next_page":
            self.pagina_Actual += 1

        elif accion_id == "prev_page" and self.pagina_Actual > 1:
            self.pagina_Actual -= 1

        elif accion_id == "ordenar":
           if self.orden_por_precio == "asc":
              self.orden_por_precio = "desc"
           else :
               self.orden_por_precio="asc"

        elif accion_id=="go_first_page":
            self.pagina_Actual=1

        elif accion_id == "filtrar_categoria":
            # Crear lista de categorías únicas
            categorias = sorted(set(item["categoria"] for item in menuCompleto))

            # Crear botones por categoría
            botones_categorias = [
                {
                    "type": "reply",
                    "reply": {"id": f"filtro_{cat.lower()}", "title": f"📁 {cat}"}
                }
                for cat in categorias
            ]

            # Crear el payload con los botones de categorías
            payload = {
                "type": "button",
                "body": {"text": "Seleccioná una categoría para filtrar el menú 👇"},
                "action": {"buttons": botones_categorias}
            }

            return payload

        # --------------------------------------------------
        # ✔️ NUEVO: Botón si el cliente quiere seguir agregando
        # --------------------------------------------------
        elif accion_id == "seguir_agregando":
            return self.generar_mensaje_menu()

        # --------------------------------------------------
        # ✔️ NUEVO: Botón para finalizar el pedido
        # --------------------------------------------------
        elif accion_id == "finalizar_pedido":
            return {
                "type": "text",
                "body": {"text": "🎉 ¡Pedido finalizado! Gracias por tu compra 🙌"}
            }

        # --------------------------------------------------
        # ✔️ Modificado: Selección de producto -> muestra botones
        # --------------------------------------------------
        elif accion_id.startswith("producto_"):
            producto_id = int(accion_id.replace("producto_", ""))

            # Obtener el producto real
            producto = next((p for p in menuCompleto if p["id"] == producto_id), None)

            if not producto:
                return {"type": "text", "body": {"text": "❌ Producto no encontrado"}}

            # mensaje con botones
            return {
                "type": "button",
                "body": {
                    "text": f"🛒 *{producto['nombre']}* agregado al carrito.\n¿Qué querés hacer ahora?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": "seguir_agregando", "title": "➕ Agregar otro producto"}
                        },
                        {
                            "type": "reply",
                            "reply": {"id": "finalizar_pedido", "title": "✔️ Finalizar pedido"}
                        }
                    ]
                }
            }

        # Retorna el mensaje actualizado del menú
        return self.generar_mensaje_menu()
