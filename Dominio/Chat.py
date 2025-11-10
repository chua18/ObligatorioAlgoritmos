from typing import Any, Dict, List
from Menu import menuCompleto

PAGE_SIZE = 5  # cantidad de productos por página

def get_paginated_menu(page: int = 1, category: str = None) -> List[Dict[str, Any]]:
    resultados = menuCompleto

    # Filtrar por categoría si se pasa
    if category:
        resultados = [item for item in resultados if item["category"].lower() == category.lower()]

    # Paginación
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    paginated = resultados[start:end]

    return paginated


class Chat:
    def __init__(self):
        self.pagina_Actual = 1
        self.categoria_Actual = None  # sin filtro por defecto

    def generar_mensaje_menu(self) -> Dict[str, Any]:
        productos = get_paginated_menu(self.pagina_Actual, self.categoria_Actual)

        # Texto del mensaje
        texto = "🍔 *Menú disponible:*\n\n"
        if not productos:
            texto += "No hay productos en esta categoría.\n"
        else:
            for p in productos:
                texto += f"- {p['nombre']} (${p['precio']})\n"

        texto += f"\n📄 Página {self.pagina_Actual}"
        if self.categoria_Actual:
            texto += f" | Filtro: {self.categoria_Actual.title()}"

        # Botones
        botones = {
            "type": "button",
            "body": {"text": texto},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "prev_page", "title": "⬅️ Anterior"}},
                    {"type": "reply", "reply": {"id": "next_page", "title": "➡️ Siguiente"}}
                ]
            }
        }

        return botones

    def manejar_accion(self, accion_id: str, category: str = None):
        # Manejo de acciones de los botones
        if accion_id == "next_page":
            self.pagina_Actual += 1
        elif accion_id == "prev_page" and self.pagina_Actual > 1:
            self.pagina_Actual -= 1
        elif accion_id.startswith("filtro_"):  # ejemplo: filtro_postres
            self.categoria_Actual = accion_id.replace("filtro_", "")
            self.pagina_Actual = 1  # reiniciamos la paginación

        # Retorna el mensaje actualizado
        return self.generar_mensaje_menu()
