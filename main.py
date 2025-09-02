import os
import time

import httpx
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from utils import NodeRedClient,TuyaBulb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    return getattr(settings, name, os.getenv(name, default))

TUYA_DEVICE_ID = 'eba6d353f959837ef0xchr';
TUYA_LOCAL_KEY = 'I24$Bo~5@{`MS>.m';
TUYA_IP        = '10.10.10.85';
TUYA_VERSION   =  3.5;

ALLOW_IP = get_setting("ALLOW_IP", "")
NODE_RED_BASE_URL = get_setting("NODE_RED_BASE_URL", "http://localhost:1880")

bulb: Optional[TuyaBulb] = None
node_red_client: Optional[NodeRedClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bulb, node_red_client
    node_red_client = NodeRedClient(NODE_RED_BASE_URL)
    try:
        bulb = TuyaBulb(TUYA_DEVICE_ID, TUYA_IP, TUYA_LOCAL_KEY, TUYA_VERSION)
        bulb.connect()
        for step in (bulb.rojo, bulb.verde, bulb.azul, bulb.blanco):
            step(); time.sleep(0.15)
        bulb.negro()
        logger.info("Bombilla Tuya inicializada correctamente.")
    except Exception as e:
        logger.error(f"Error inicializando Tuya: {e}")
        bulb = None  # evita usar una bombilla en estado inconsistente

    yield
    if bulb:
        try:
            bulb.off()
        except Exception:
            pass

app = FastAPI(
    title="Python API with Node-RED & Tuya Integration",
    description="API that communicates with Node-RED and controls a Tuya LED bulb",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COLOR_MAP = {
    "A": "verde",
    "V": "rojo",
    "B": "azul",
    "R": "blanco",
}

def apply_code(code: str) -> str:
    if bulb is None:
        raise RuntimeError("Bombilla Tuya no inicializada")

    code = (code or "").strip().upper()
    name = COLOR_MAP.get(code, "negro")

    if code == "A":
        bulb.blink(bulb.verde)
    elif code == "V":
        bulb.blink(bulb.rojo)
    elif code == "B":
        bulb.blink(bulb.azul)
    elif code == "R":
        bulb.blink(bulb.blanco)
    else:
        bulb.negro()
    return name

def parse_user_string_from_xml(raw: bytes) -> str:
    root = ET.fromstring(raw)
    node = root.find("UserString")
    if node is None or node.text is None:
        raise ValueError("No se encontró <UserString> en el XML")
    return node.text.strip()

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@app.get("/")
async def root():
    return {
        "message": "Python API is running",
        "status": "healthy",
        "node_red_url": NODE_RED_BASE_URL,
        "tuya_initialized": bulb is not None,
        "timestamp": utc_now_iso(),
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        assert node_red_client is not None
        node_red_status = await node_red_client.check_connection()
        return {
            "api_status": "healthy",
            "node_red_status": node_red_status,
            "tuya_initialized": bulb is not None,
            "timestamp": utc_now_iso(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    
@app.get("/api/sensors")
async def get_sensor_data():
    try:
        assert node_red_client is not None
        data = await node_red_client.get_data("sensors")
        return {
            "success": True,
            "sensors": data,
            "timestamp": utc_now_iso(),
        }
    except Exception as e:
        logger.error(f"Error fetching sensor data: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch sensor data")

@app.get("/symphony")
async def symphony_legacy(request: Request, background: BackgroundTasks):
    if ALLOW_IP and request.client and request.client.host != ALLOW_IP:
        raise HTTPException(status_code=403, detail="Origen no permitido")
    raw = await request.body()
    if not raw:
        raise HTTPException(status_code=400, detail="Body vacío")
    if bulb is None:
        raise HTTPException(status_code=503, detail="Bombilla no inicializada")
    try:
        user_string = parse_user_string_from_xml(raw)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"XML inválido: {e}")

    logger.info(f"symphony: {user_string}")
    background.add_task(apply_code, user_string)
    return {"ok": True,"user_string": user_string,"color": COLOR_MAP.get(user_string.upper(), "negro"),"timestamp": utc_now_iso(),}

@app.get("/api/tuya/symphony")
async def symphony_api(request: Request, background: BackgroundTasks):
    return await symphony_legacy(request, background)  # reusa la lógica

@app.get("/api/tuya/test")
async def tuya_test(background: BackgroundTasks):
    if bulb is None:
        raise HTTPException(status_code=503, detail="Bombilla no inicializada")
    def seq():
        for step in (bulb.rojo, bulb.verde, bulb.azul, bulb.blanco):
            step(); time.sleep(0.5)
        bulb.negro()
    background.add_task(seq)
    return {"ok": True, "message": "Secuencia de prueba lanzada", "timestamp": utc_now_iso()}

@app.get("/api/tuya/code/{code}")
async def tuya_code(code: str, background: BackgroundTasks):
    if bulb is None:
        raise HTTPException(status_code=503, detail="Bombilla no inicializada")
    c = (code or "").upper()
    background.add_task(apply_code, c)
    return {"ok": True, "code": c, "color": COLOR_MAP.get(c, "negro"), "timestamp": utc_now_iso()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)