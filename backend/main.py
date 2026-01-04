from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import engine, SessionLocal, get_db
from engine import bot_instance
import threading
import time
import pandas as pd
import io
import re

# Cria tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WORKER ---
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

# --- ROTAS BASICAS ---
@app.get("/")
def read_root():
    return {"message": "Backend Online", "status": "online"}

@app.post("/bot/start")
def start_bot():
    return bot_instance.start()

@app.post("/bot/stop")
def stop_bot():
    return bot_instance.stop()

@app.get("/bot/status")
def get_bot_status():
    return {"is_running": bot_instance.is_running}

# --- ROTAS DE GRUPOS E IMPORTACAO ---

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
        
        match = re.search(r"\[(.*?)\]", raw_name)
        
        if match:
            group_name = match.group(1).upper()
            clean_name = raw_name
        else:
            group_name = "GERAL"
            clean_name = raw_name

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

# --- NOVA ROTA DE BROADCAST ---
@app.post("/broadcast")
def create_broadcast(broadcast: schemas.BroadcastCreate, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).filter(models.Contact.group_id == broadcast.group_id).all()
    
    if not contacts:
        return {"status": "error", "message": "Este grupo esta vazio!"}

    count = 0
    for contact in contacts:
        new_msg = models.Message(
            connection_id=broadcast.connection_id,
            phone_dest=contact.phone,
            content=broadcast.content,
            status="pending"
        )
        db.add(new_msg)
        count += 1
    
    db.commit()
    return {"status": "success", "queued": count, "message": f"Campanha criada! {count} mensagens na fila."}


# --- DEMAIS ROTAS ---

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
