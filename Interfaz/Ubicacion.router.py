from fastapi import APIRouter 
from Dominio.Ubicacion import Ubicacion

router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])

ubicaciones = []

@router.post("/")
def crear_ubicscion(x: int, y: str):
    nuevo = Ubicacion(x, y)
    ubicaciones.append(nuevo)
    return {"mensaje": f"Ubicacion ({x},{y}) creada correctamente",
           "ubicacion": {"x": nuevo.x, "y": nuevo.y}
           }
        