from Menu import menuCompleto
from typing import Any, Dict, List

PAGE_SIZE = 5  # cantidad de productos por página

def get_paginated_menu(page: int = 1, category: str = None) -> List[Dict[str, Any]]:
    # 1. Partimos del menú completo
    resultados = menuCompleto

    # 2. Aplicamos filtro por categoría si se pasa
    if category:
        resultados = [item for item in resultados if item["category"].lower() == category.lower()]

    # 3. Paginamos los resultados filtrados
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    paginated = resultados[start:end]

    return paginated
