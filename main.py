from fastapi import FastAPI, HTTPException, Request
from utils.get_message_type import get_message_type
import os
import logging
import httpx
from typing import Any, Dict, List
from Dominio.Chat import Chat

chat = Chat()

app = FastAPI()

# --- CREDENCIALES Y CONFIGURACIÓN ---
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
VERSION = os.getenv("VERSION", "v22.0")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
RECIPIENT_PHONE = os.getenv("RECIPIENT_PHONE", "")

GRAPH_SEND_URL = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

logging.info(f"ACCESS_TOKEN cargado? {bool(ACCESS_TOKEN)}")
logging.info(f"PHONE_NUMBER_ID: {PHONE_NUMBER_ID!r}")
logging.info(f"GRAPH_SEND_URL: {GRAPH_SEND_URL}")

# --------------------------------------------------------
# FUNCIONES AUXILIARES PARA ENVIAR MENSAJES A WHATSAPP
# --------------------------------------------------------
async def send_to_whatsapp(payload: Dict[str, Any]) -> None:
    """Envía un mensaje a la API de WhatsApp usando httpx (async)."""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        logging.warning("Falta ACCESS_TOKEN o PHONE_NUMBER_ID. (No se envía a la API, modo MOCK)")
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
    msg = chat.generar_mensaje_menu()
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": msg
    }
    print(f"payload del menú paginado:\n{payload}")
    await send_to_whatsapp(payload)


# --------------------------------------------------------
# HELPER PARA ARMAR EL PAYLOAD SEGÚN EL TIPO
# --------------------------------------------------------
def build_whatsapp_payload(to: str, msg: Dict[str, Any]) -> Dict[str, Any]:
    msg_type = msg.get("type")

    # --- Si es un mensaje de texto ---
    if msg_type == "text":
        return {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": msg["body"]
        }

    # --- Si es un mensaje con botones ---
    if msg_type == "button":
        return {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": msg["body"],
                "action": msg["action"]
            }
        }

    # --- Cualquier lista interactiva ---
    if msg_type == "list":
        return {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": msg
        }

    # Fallback
    return {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": msg
    }



# --------------------------------------------------------
# ENDPOINTS
# --------------------------------------------------------
@app.get("/")
def root():
    return {"mensaje": "API de WhatsApp funcionando correctamente"}


@app.get("/welcome")
def index():
    return {"mensaje": "welcome developer"}


@app.get("/whatsapp")
async def verify_webhook(request: Request):
    """Endpoint de verificación del webhook de WhatsApp"""
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    raise HTTPException(status_code=403, detail="Token inválido o parámetros faltantes")


@app.post("/whatsapp")
async def received_message(request: Request):
    """Endpoint para recibir mensajes de WhatsApp"""
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

            # --- LÓGICA DE MANEJO DE ACCIONES ---
            if (
                content == "next_page" or
                content == "prev_page" or
                content == "ordenar" or
                content == "filtrar_categoria" or
                content == "go_first_page" or
                content == "seguir_agregando" or
                content == "finalizar_pedido" or
                content.startswith("producto_") or
                content.startswith("filtro_")
            ):
                # Delega toda la lógica en Chat.manejar_accion
                nuevo_mensaje = chat.manejar_accion( 
                    accion_id=content,
                    cliente=number,
                    ubicacion=(0.0, 0.0)
                )

                # Armamos el payload según el tipo (text, button o interactive list)
                payload = build_whatsapp_payload(number, nuevo_mensaje)
                await send_to_whatsapp(payload)

            else:
                # Primer mensaje, texto cualquiera o ID no reconocida → mostrar menú inicial
                await send_menu(number, name)

        return "EVENT_RECEIVED"

    except Exception as e:
        print("Error en /whatsapp:", e)
        # Es vital que el endpoint devuelva 200 OK a WhatsApp aunque falle internamente
        # para evitar reenvíos.
        return "EVENT_RECEIVED"


# --------------------------------------------------------
# MAIN SERVER
# --------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    # ✅ Usa el puerto de Railway dinámicamente
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)