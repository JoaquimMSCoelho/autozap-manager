from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import engine, get_db

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

@app.get("/")
def read_root():
    return {"message": "Backend Online", "status": "online"}

# --- ROTAS CONEXOES ---
@app.get("/connections", response_model=List[schemas.ConnectionResponse])
def list_connections(db: Session = Depends(get_db)):
    return db.query(models.Connection).filter(models.Connection.is_active == True).all()

@app.post("/connections", response_model=schemas.ConnectionResponse)
def create_connection(connection: schemas.ConnectionCreate, db: Session = Depends(get_db)):
    db_conn = models.Connection(name=connection.name, phone_number=connection.phone_number)
    db.add(db_conn)
    db.commit()
    db.refresh(db_conn)
    return db_conn

@app.delete("/connections/{connection_id}")
def delete_connection(connection_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Connection).filter(models.Connection.id == connection_id).first()
    if c:
        c.is_active = False
        db.commit()
    return {"status": "ok"}

# --- ROTAS MENSAGENS ---
@app.get("/messages", response_model=List[schemas.MessageResponse])
def list_messages(db: Session = Depends(get_db)):
    return db.query(models.Message).order_by(models.Message.created_at.desc()).limit(100).all()

@app.post("/messages", response_model=schemas.MessageResponse)
def create_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    new_msg = models.Message(connection_id=msg.connection_id, phone_dest=msg.phone_dest, content=msg.content)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

# --- ROTAS CONFIGURACOES (NOVO) ---
@app.get("/configs", response_model=List[schemas.ConfigResponse])
def list_configs(db: Session = Depends(get_db)):
    return db.query(models.SystemConfig).all()

@app.post("/configs", response_model=schemas.ConfigResponse)
def update_config(config: schemas.ConfigCreate, db: Session = Depends(get_db)):
    # Tenta achar a config pelo nome da chave
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
