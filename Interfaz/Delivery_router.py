from fastapi import APIRouter 
from Dominio.Delivery import Delivery

router = APIRouter(prefix="/deliverys", tags=["Deliverys"])

deliverys = []

@router.post("/")
def crear_delivery(id: int, nombre: str):
    nuevo = Delivery(id, nombre)
    deliverys.append(nuevo)
    return {"mensaje": f"Delivery {nombre} creado correctamente"}
