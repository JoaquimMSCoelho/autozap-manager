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
    status: str = "active"
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

# --- Configuracoes ---
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

# --- GRUPOS E CONTATOS ---
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupResponse(GroupBase):
    id: int
    contact_count: int = 0
    class Config:
        from_attributes = True

class ContactBase(BaseModel):
    name: str
    phone: str

class ContactCreate(ContactBase):
    group_id: int

class ContactResponse(ContactBase):
    id: int
    group_id: int
    class Config:
        from_attributes = True

# --- BROADCAST ---
class BroadcastCreate(BaseModel):
    group_id: int
    content: str
    connection_id: int
