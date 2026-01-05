import sys
import os
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models
import schemas
from database import engine, SessionLocal, get_db
from engine import bot_instance
import threading
import time
import pandas as pd
import io
import re
import uvicorn # <--- IMPORTANTE: Adicionado para rodar o servidor

# --- CONFIGURACAO INICIAL ---
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWN_PREFIXES = [
    "ADVR", "ADSE", "IRPF", "IRNF", "PRGS", "UBER", 
    "INF", "MEI", "FAM", "DEP", "SIC", "LAN", "MAN", "NIP", 
    "AD", "IR"
]

# --- WORKER (ROBO EM PLANO DE FUNDO) ---
def background_worker():
    while True:
        if bot_instance.is_running:
            db = SessionLocal()
            try:
                msg = db.query(models.Message).filter(models.Message.status == "pending").first()
                if msg:
                    print(f"[WORKER] Enviando para {msg.phone_dest}...")
                    config_interval = db.query(models.SystemConfig).filter(models.SystemConfig.key_name == "message_interval").first()
                    wait_time = int(config_interval.value) if config_interval else 15

                    result = bot_instance.send_message(msg.phone_dest, msg.content)
                    
                    if result["status"] == "sent":
                        msg.status = "sent"
                    else:
                        msg.status = "error"
                    
                    db.commit()
                    time.sleep(wait_time)
                else:
                    time.sleep(2)
            except Exception as e:
                print(f"[WORKER ERROR] {str(e)}")
                time.sleep(5)
            finally:
                db.close()
        else:
            time.sleep(1)

worker_thread = threading.Thread(target=background_worker, daemon=True)
worker_thread.start()

# --- ROTAS DA API ---

@app.post("/bot/start")
def start_bot():
    return bot_instance.start()

@app.post("/bot/stop")
def stop_bot():
    return bot_instance.stop()

@app.get("/bot/status")
def get_bot_status():
    return {"is_running": bot_instance.is_running}

@app.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_sent_today = db.query(models.Message).filter(models.Message.status == "sent", models.Message.created_at >= today_start).count()
    total_pending = db.query(models.Message).filter(models.Message.status == "pending").count()
    total_error_today = db.query(models.Message).filter(models.Message.status == "error", models.Message.created_at >= today_start).count()
    next_queue = db.query(models.Message).filter(models.Message.status == "pending").limit(3).all()

    return {
        "sent_today": total_sent_today,
        "pending": total_pending,
        "error_today": total_error_today,
        "is_running": bot_instance.is_running,
        "next_in_queue": next_queue
    }

@app.post("/import-contacts")
async def import_contacts(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
    df.columns = [c.lower() for c in df.columns]
    count_new = 0
    for index, row in df.iterrows():
        raw_name = str(row.get('nome', ''))
        phone = str(row.get('telefone', ''))
        group_name = "GERAL" 
        clean_name = raw_name
        match = re.search(r"\[(.*?)\]", raw_name)
        if match:
            group_name = match.group(1).upper()
        else:
            name_upper = raw_name.upper()
            for sigla in KNOWN_PREFIXES:
                if sigla in name_upper:
                    group_name = sigla
                    break
        group = db.query(models.Group).filter(models.Group.name == group_name).first()
        if not group:
            group = models.Group(name=group_name, description="Importado Automaticamente")
            db.add(group)
            db.commit()
            db.refresh(group)
        contact = db.query(models.Contact).filter(models.Contact.phone == phone).first()
        if not contact:
            contact = models.Contact(name=clean_name, phone=phone, group_id=group.id)
            db.add(contact)
            count_new += 1
        else:
            contact.group_id = group.id
            contact.name = clean_name
        db.commit()
    return {"status": "success", "imported": count_new, "message": "Processamento concluido"}

@app.get("/groups", response_model=List[schemas.GroupResponse])
def list_groups(db: Session = Depends(get_db)):
    groups = db.query(models.Group).all()
    for g in groups:
        g.contact_count = db.query(models.Contact).filter(models.Contact.group_id == g.id).count()
    return groups

@app.get("/contacts/{group_id}", response_model=List[schemas.ContactResponse])
def list_contacts_by_group(group_id: int, db: Session = Depends(get_db)):
    return db.query(models.Contact).filter(models.Contact.group_id == group_id).all()

@app.post("/broadcast")
def create_broadcast(broadcast: schemas.BroadcastCreate, db: Session = Depends(get_db)):
    if broadcast.group_id == -1:
        contacts = db.query(models.Contact).all()
    else:
        contacts = db.query(models.Contact).filter(models.Contact.group_id == broadcast.group_id).all()
    if not contacts:
        return {"status": "error", "message": "Nenhum contato encontrado!"}
    count = 0
    for contact in contacts:
        new_msg = models.Message(connection_id=broadcast.connection_id, phone_dest=contact.phone, content=broadcast.content, status="pending")
        db.add(new_msg)
        count += 1
    db.commit()
    dest_name = "TODOS" if broadcast.group_id == -1 else "Grupo"
    return {"status": "success", "queued": count, "message": f"Campanha para {dest_name} criada! {count} mensagens na fila."}

@app.get("/messages", response_model=List[schemas.MessageResponse])
def list_messages(db: Session = Depends(get_db)):
    return db.query(models.Message).order_by(models.Message.created_at.desc()).limit(100).all()

@app.post("/messages", response_model=schemas.MessageResponse)
def create_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    new_msg = models.Message(connection_id=msg.connection_id, phone_dest=msg.phone_dest, content=msg.content, status="pending")
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

@app.get("/configs", response_model=List[schemas.ConfigResponse])
def list_configs(db: Session = Depends(get_db)):
    return db.query(models.SystemConfig).all()

@app.post("/configs", response_model=schemas.ConfigResponse)
def update_config(config: schemas.ConfigCreate, db: Session = Depends(get_db)):
    existing = db.query(models.SystemConfig).filter(models.SystemConfig.key_name == config.key_name).first()
    if existing:
        existing.value = config.value
        existing.is_active = config.is_active
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_config = models.SystemConfig(key_name=config.key_name, value=config.value, is_active=config.is_active)
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config

# --- SERVIR O FRONTEND (ESTATICO) ---
# Logica Hibrida: Funciona no VS Code E no .EXE

if getattr(sys, 'frozen', False):
    # MODO .EXE (Producao)
    base_path = os.path.dirname(sys.executable)
    frontend_path = os.path.join(base_path, "frontend", "dist")
    print(f"[INFO] Modo EXE detectado. Buscando site em: {frontend_path}")
else:
    # MODO DEV (VS Code)
    base_path = os.path.dirname(os.path.dirname(__file__))
    frontend_path = os.path.join(base_path, "frontend", "dist")
    print(f"[INFO] Modo DEV detectado. Buscando site em: {frontend_path}")

if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("bot/") or full_path.startswith("messages"):
             raise HTTPException(status_code=404, detail="API route not found")
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    print("AVISO CRITICO: Pasta frontend/dist nao encontrada.")
    print(f"O sistema esperava encontrar em: {frontend_path}")

# --- IGNICAO DO MOTOR (NOVO!) ---
# Isso garante que o servidor inicie quando rodar o .EXE
if __name__ == "__main__":
    # Roda na porta 8000 e aceita conexoes locais
    uvicorn.run(app, host="127.0.0.1", port=8000)