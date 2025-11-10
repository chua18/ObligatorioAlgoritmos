from fastapi import FastAPI, HTTPException, Request
from utils.get_message_type import get_message_type

# --- NUEVO ---
from Menu import menuCompleto
import os
import logging
import httpx
from typing import Any, Dict, List
from Dominio.Chat import Chat
chat = Chat()
  # <- categorías desde menu.py

app = FastAPI()

# ---------------- Helpers de MENÚ (NUEVO) ----------------
def build_category_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    # WhatsApp List: máx 10 filas por sección
    for c in menuCompleto[:5]:
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
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")          # Page Access Token
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")    # phone_number_id
GRAPH_SEND_URL ="https://graph.facebook.com/v22.0/828302067035331/messages"


async def send_to_whatsapp(payload: Dict[str, Any]) -> None:
    """Envía un mensaje a la API de WhatsApp usando httpx (async)."""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        logging.warning("Falta WHATSAPP_TOKEN o WHATSAPP_PHONE_ID. (No se envía a la API, modo MOCK)")
        logging.info(f"MOCK SEND => {payload}")
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
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
    """Envía el menú actual (paginado) al usuario."""
    # Genera el mensaje con los botones desde Chat
    msg = chat.generar_mensaje_menu()

    # Adaptamos para enviar a WhatsApp
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": msg  # <- el diccionario que genera Chat
    }

    print(f"payload del menú paginado:\n{payload}")
    await send_to_whatsapp(payload)


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
        body = await request.json()
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value and len(value["messages"]) > 0:
            message = value["messages"][0]
            type_message, content = get_message_type(message)
            number = message["from"]
            contacts = value.get("contacts", [])
            name = contacts[0].get("profile", {}).get("name", "Cliente") if contacts else "Cliente"

            print(f"Mensaje recibido de {number}: {content}")

            # --- acá entra la lógica de Chat ---
            if content in ["➡️ Siguiente", "⬅️ Anterior"]:
                # Mover página
                if content == "➡️ Siguiente":
                    nuevo_mensaje = chat.manejar_accion("next_page")
                else:
                    nuevo_mensaje = chat.manejar_accion("prev_page")
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": number,
                    "type": "interactive",
                    "interactive": nuevo_mensaje
                }
                await send_to_whatsapp(payload)
            
            else:
                # Primer mensaje o texto cualquiera → mostrar menú inicial
                await send_menu(number, name)

        return "EVENT_RECEIVED"

    except Exception as e:
        print("Error en /whatsapp:", e)
        return "EVENT_RECEIVED"

    
if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app,host="0.0.0.0",port=8000)
