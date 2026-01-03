from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import engine, SessionLocal, get_db
from engine import bot_instance
import threading
import time

# Cria tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configura CORS
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WORKER (O FUNCIONARIO INVISIVEL) ---
def background_worker():
    while True:
        # 1. Verifica se o robo esta ligado
        if bot_instance.is_running:
            db = SessionLocal()
            try:
                # 2. Busca mensagem pendente mais antiga
                msg = db.query(models.Message).filter(models.Message.status == "pending").first()
                
                if msg:
                    print(f"[WORKER] Enviando para {msg.phone_dest}...")
                    
                    # 3. Busca configuracao de intervalo
                    config_interval = db.query(models.SystemConfig).filter(models.SystemConfig.key_name == "message_interval").first()
                    wait_time = int(config_interval.value) if config_interval else 15

                    # 4. Envia usando o motor
                    result = bot_instance.send_message(msg.phone_dest, msg.content)
                    
                    # 5. Atualiza status
                    if result["status"] == "sent":
                        msg.status = "sent"
                    else:
                        msg.status = "error"
                        print(f"[ERRO] {result['message']}")
                    
                    db.commit()
                    
                    # 6. Espera o intervalo antes da proxima
                    print(f"[WORKER] Aguardando {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    # Sem mensagens, dorme um pouco para nao gastar CPU
                    time.sleep(2)
            
            except Exception as e:
                print(f"[WORKER ERROR] {str(e)}")
                time.sleep(5)
            finally:
                db.close()
        else:
            # Robo desligado, checa novamente em 1s
            time.sleep(1)

# Inicia o worker em uma thread separada ao iniciar a API
worker_thread = threading.Thread(target=background_worker, daemon=True)
worker_thread.start()

# --- ROTAS ---

@app.get("/")
def read_root():
    return {"message": "Backend e Worker Online", "status": "online"}

@app.post("/bot/start")
def start_bot():
    return bot_instance.start()

@app.post("/bot/stop")
def stop_bot():
    return bot_instance.stop()

@app.get("/bot/status")
def get_bot_status():
    return {"is_running": bot_instance.is_running}

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

@app.get("/messages", response_model=List[schemas.MessageResponse])
def list_messages(db: Session = Depends(get_db)):
    return db.query(models.Message).order_by(models.Message.created_at.desc()).limit(100).all()

# ROTA ALTERADA: Agora apenas AGENDA, nao envia na hora
@app.post("/messages", response_model=schemas.MessageResponse)
def create_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    new_msg = models.Message(
        connection_id=msg.connection_id, 
        phone_dest=msg.phone_dest, 
        content=msg.content,
        status="pending" # Sempre entra como pendente
    )
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
