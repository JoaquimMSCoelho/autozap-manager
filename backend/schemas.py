from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Conexoes ---
class ConnectionBase(BaseModel):
    name: str
    phone_number: Optional[str] = None

class ConnectionCreate(ConnectionBase):
    pass

class ConnectionResponse(ConnectionBase):
    id: int
    status: str
    is_active: bool
    class Config:
        from_attributes = True

# --- Mensagens ---
class MessageBase(BaseModel):
    phone_dest: str
    content: str

class MessageCreate(MessageBase):
    connection_id: int

class MessageResponse(MessageBase):
    id: int
    status: str
    created_at: datetime
    connection_id: int
    class Config:
        from_attributes = True

# --- Configuracoes (NOVO) ---
class ConfigBase(BaseModel):
    key_name: str
    value: str
    is_active: bool = True

class ConfigCreate(ConfigBase):
    pass

class ConfigResponse(ConfigBase):
    id: int
    class Config:
        from_attributes = True
