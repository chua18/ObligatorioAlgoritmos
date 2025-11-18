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
VERSION = os.getenv("VERSION", "v22.0")

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


# NOTA: En un entorno de producción, ACCESS_TOKEN debe venir de os.getenv
ACCESS_TOKEN = "EAA9eDvNAZBDQBP37gpXOtr2GEcSy83sotyZA5s1qRZBFqWZBmFOuTglbfCASLaD1vV1rdOgyJBHKAxRdk8JRlTxcs7ZBCGeQ0vxhne9nlV08EKkpbz34q3wgeV8Pb3vmcajZCdjB2U5lOy23JRwfrhGagM2MtQUeaalUGtQ3FFIP7inKeENVP8wC7vPc34QQZDZD"


@app.get("/whatsapp")
async def verify_token(request: Request):
    try:
        query_params = request.query_params
        verify_token = query_params.get("hub.verify_token")
        challenge = query_params.get("hub.challenge")

        # Usar la variable de entorno para el token de verificación
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

            # --- LÓGICA CORREGIDA ---
            # Todas las acciones del menú (botones/listas) tienen un ID (content)
            # que comienza con alguna de estas IDs
            
            if (
                content == "next_page" or
                content == "prev_page" or
                content == "ordenar" or
                content == "filtrar_categoria" or
                content == "go_first_page" or
                content == "seguir_agregando" or
                content == "finalizar_pedido" or
                content.startswith("producto_") or
                content.startswith("filtro_") # ✅ Maneja la respuesta de la selección de categoría
            ):
                # Delega toda la lógica en Chat.manejar_accion
                # Ahora maneja_accion acepta estos argumentos (corregido en Chat.py)
                nuevo_mensaje = chat.manejar_accion( 
                    accion_id=content,
                    cliente=number,
                    ubicacion=(0.0, 0.0) # Usar ubicación por defecto por ahora
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
    uvicorn.run(app, host="0.0.0.0", port=8000)