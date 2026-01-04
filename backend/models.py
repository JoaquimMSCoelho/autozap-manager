from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# --- TABELAS DO SISTEMA ---

class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("connections.id"))
    phone_dest = Column(String, index=True)
    content = Column(Text)
    status = Column(String, default="pending") # pending, sent, error
    created_at = Column(DateTime, default=datetime.now)

class SystemConfig(Base):
    __tablename__ = "system_configs"
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, unique=True, index=True) # ex: message_interval
    value = Column(String)
    is_active = Column(Boolean, default=True)

# --- NOVAS TABELAS (SEGMENTACAO) ---

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # ex: INF, AD, GERAL
    description = Column(String, nullable=True)
    
    # Relacionamento: Um grupo tem varios contatos
    contacts = relationship("Contact", back_populates="group")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True) # O numero eh unico
    
    # Relacionamento: Um contato pertence a um grupo
    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship("Group", back_populates="contacts")
