from fastapi import FastAPI, HTTPException, Request
from utils.get_message_type import get_message_type
import os
import logging
import httpx
from typing import Any, Dict, List
from Dominio.Chat import Chat  # ddddee

chat = Chat()

app = FastAPI()

# --- CREDENCIALES Y CONFIGURACIÓN ---
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
GRAPH_SEND_URL = "https://graph.facebook.com/v22.0/828302067035331/messages"


# --------------------------------------------------------
# FUNCIONES AUXILIARES PARA ENVIAR MENSAJES A WHATSAPP
# --------------------------------------------------------
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
# 🔧 NUEVO: helper para armar el payload según el tipo
# --------------------------------------------------------
def build_whatsapp_payload(to: str, msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recibe el dict que devuelve Chat (list/button/text)
    y lo transforma en el payload correcto para la API de WhatsApp.
    """
    msg_type = msg.get("type")

    # Mensaje de texto simple
    if msg_type == "text":
        texto = msg["body"]["text"]
        return {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": texto
            }
        }

    # Cualquier otro ("list", "button", etc.) va como interactive
    return {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": msg
    }


# --------------------------------------------------------
# el main cambio
# --------------------------------------------------------
@app.get("/welcome")
def index():
    return {"mensaje": "welcome developer"}


ACCESS_TOKEN = "EAA9eDvNAZBDQBP37gpXOtr2GEcSy83sotyZA5s1qRZBFqWZBmFOuTglbfCASLaD1vV1rdOgyJBHKAxRdk8JRlTxcs7ZBCGeQ0vxhne9nlV08EKkpbz34q3wgeV8Pb3vmcajZCdjB2U5lOy23JRwfrhGagM2MtQUeaalUGtQ3FFIP7inKeENVP8wC7vPc34QQZDZD"


@app.get("/whatsapp")
async def verify_token(request: Request):
    try:
        query_params = request.query_params
        verify_token = query_params.get("hub.verify_token")
        challenge = query_params.get("hub.challenge")

        if verify_token is not None and challenge is not None and verify_token == ACCESS_TOKEN:
            return int(challenge)
        else:
            raise HTTPException(status_code=400, detail="Token de verificación inválido o parámetros faltantes")

    except Exception as e:
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

            # --- NUEVA LÓGICA CORREGIDA ---
            # WhatsApp List/Button devuelve el ID del row (no el texto)
            acciones_menu = [
                "next_page",
                "prev_page",
                "ordenar",
                "filtrar_categoria",
                "go_first_page",
                "seguir_agregando",
                "finalizar_pedido",
            ]

            if (
                content in acciones_menu
                or content.startswith("producto_")  # selección de producto de la lista
            ):
                # Delega toda la lógica en Chat.manejar_accion
                nuevo_mensaje = chat.manejar_accion(   # ⬅️⬅️ AQUÍ EL CAMBIO
                    accion_id=content,
                    cliente=number,
                    ubicacion=(0.0, 0.0)
                )

                # Armamos el payload según el tipo (text o interactive)
                payload = build_whatsapp_payload(number, nuevo_mensaje)
                await send_to_whatsapp(payload)

            else:
                # Primer mensaje o texto cualquiera → mostrar menú inicial
                await send_menu(number, name)

        return "EVENT_RECEIVED"

    except Exception as e:
        print("Error en /whatsapp:", e)
        return "EVENT_RECEIVED"


# --------------------------------------------------------
# MAIN SERVER
# --------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
