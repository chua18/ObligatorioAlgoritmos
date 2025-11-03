from fastapi import APIRouter 
from Dominio.Producto import Producto

router = APIRouter(prefix="/productos", tags=["Productos"])

productos = []

@router.post("/")
def crear_producto(id: int, nombre: str, categoria:str,precio:str):
    nuevo = Producto(id, nombre,categoria,precio)
    productos.append(nuevo)
    return {"mensaje": f"Producto {id} creado correctamente"}
