from fastapi import FastAPI, HTTPException, Request
from utils.get_message_type import get_message_type

# --- NUEVO ---
import os
import logging
import httpx
from typing import Any, Dict, List


from Menu import menu_categorias  # <- categorías desde menu.py

app = FastAPI()

# ---------------- Helpers de MENÚ (NUEVO) ----------------
def build_category_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    # WhatsApp List: máx 10 filas por sección
    for c in menu_categorias[:10]:
        rows.append({
            "id": f"CAT_{c['id']}",
            "title": c["title"],
            "description": "Ver productos de esta categoría" if c["id"] != "Todos" else "Ver todo el catálogo"
        })
    return rows

def build_list_message(to: str, body_text: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": "Ver menú",
                "sections": [
                    {"title": "Categorías", "rows": rows}
                ]
            }
        }
    }

# --- NUEVO: credenciales y envío a WhatsApp ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")          # Page Access Token
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")    # phone_number_id
GRAPH_SEND_URL = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"


async def send_to_whatsapp(payload: Dict[str, Any]) -> None:
    """Envía un mensaje a la API de WhatsApp usando httpx (async)."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logging.warning("Falta WHATSAPP_TOKEN o WHATSAPP_PHONE_ID. (No se envía a la API, modo MOCK)")
        logging.info(f"MOCK SEND => {payload}")
        return

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(GRAPH_SEND_URL, json=payload, headers=headers)
            if response.status_code >= 300:
                logging.error(f"Error al enviar a WhatsApp: {response.status_code} {response.text}")
            else:
                logging.info(f"Enviado a WhatsApp: {response.json()}")
        except httpx.RequestError as e:
            logging.error(f"Error de conexión al enviar a WhatsApp: {e}")


async def send_menu(to: str, nombre: str = "Cliente") -> None:
    """Envía el menú principal al usuario."""
    rows = build_category_rows()
    msg = build_list_message(
        to=to,
        body_text=f"Hola {nombre} 👋\nElegí una categoría para ver el menú:",
        rows=rows
    )
    print(f"payload del menu:\n{msg}")
    await send_to_whatsapp(msg)
# ---------------- FIN Helpers de MENÚ ----------------


@app.get("/welcome")
def index():
    return {"mensaje": "welcome developer"}

ACCESS_TOKEN = "EAA9eDvNAZBDQBP37gpXOtr2GEcSy83sotyZA5s1qRZBFqWZBmFOuTglbfCASLaD1vV1rdOgyJBHKAxRdk8JRlTxcs7ZBCGeQ0vxhne9nlV08EKkpbz34q3wgeV8Pb3vmcajZCdjB2U5lOy23JRwfrhGagM2MtQUeaalUGtQ3FFIP7inKeENVP8wC7vPc34QQZDZD" 

@app.get("/whatsapp")
async def verify_token(request: Request):
    try:
        # Obtener los parámetros de la URL (query parameters)
        query_params = request.query_params

        # Extraer el token de verificación y el desafío (challenge)
        verify_token = query_params.get("hub.verify_token")
        challenge = query_params.get("hub.challenge")

        # 1. Comprobar si los parámetros están presentes
        # 2. Comprobar si el token de verificación coincide con el token predefinido
        if verify_token is not None and challenge is not None and verify_token == ACCESS_TOKEN:
            # Si coincide, se devuelve el desafío (challenge) como un entero
            return int(challenge)
        else:
            # Si no coincide o faltan parámetros, se lanza un error HTTP 400
            raise HTTPException(status_code=400, detail="Token de verificación inválido o parámetros faltantes")

    except Exception as e:
        # Manejo de errores generales durante el proceso
        raise HTTPException(status_code=400, detail=f"Error en la verificación: {e}")

@app.post("/whatsapp")
async def received_message(request: Request):
    try:
        # Lee el cuerpo de la solicitud POST como JSON
        body = await request.json()

        # Navegación básica en la estructura JSON del webhook de Meta
        # La estructura puede variar, esto es un acceso inicial típico
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # Verifica si hay mensajes reales dentro de la carga útil
        if "messages" in value and len(value["messages"]) > 0:
            # Extrae el primer mensaje de la lista de mensajes
            type_message, content = get_message_type(value["messages"][0])
            
            message = value["messages"][0]
            # Extrae el número de teléfono del remitente
            number = message["from"]
            print(f"Mensaje recibido de {number}: Tipo: {type_message}, Contenido: {content}")

            # --- NUEVO: obtener nombre del contacto si está disponible ---
            contacts = value.get("contacts", [])
            name = contacts[0].get("profile", {}).get("name", "Cliente") if contacts else "Cliente"

            # --- NUEVO: responder con el menú ---
            await send_menu(number, name)

        # Aquí podrías agregar lógica adicional para procesar el mensaje recibido
        
        # Es crucial retornar un código HTTP 200 (implícito aquí)
        # o un mensaje de éxito para que Meta no reintente el envío.
        return "EVENT_RECEIVED"

    except Exception:
        # En caso de error, todavía se recomienda devolver una respuesta de éxito (200)
        # para evitar reintentos continuos, aunque se debe registrar el error.
        return "EVENT_RECEIVED"
    
if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app,host="0.0.0.0",port=8000)
