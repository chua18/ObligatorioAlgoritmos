from fastapi import APIRouter 
from Dominio.Pedido import Pedido

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

pedidos = []

@router.post("/")
def crear_pedido(id: int, cliente: str, ubicacion:str,comidas:str):
    nuevo = Pedido(id, cliente,ubicacion,comidas)
    pedidos.append(nuevo)
    return {"mensaje": f"Pedido {id} creado correctamente"}
