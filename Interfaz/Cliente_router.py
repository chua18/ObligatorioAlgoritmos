from fastapi import APIRouter 
from Dominio.Cliente import Cliente

router = APIRouter(prefix="/clientes", tags=["Clientes"])

clientes = []

@router.post("/")
def crear_cliente(id: int, nombre: str, numero: str, ubicacion:str):
    nuevo = Cliente(id, nombre, numero,ubicacion)
    clientes.append(nuevo)
    return {"mensaje": f"Cliente {nombre} creado correctamente"}
