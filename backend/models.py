from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class SystemConfig(Base):
    __tablename__ = "system_configs"
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, unique=True, index=True)
    value = Column(String)
    is_active = Column(Boolean, default=True)

class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String)
    status = Column(String, default="disconnected")
    session_file = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relacionamento com mensagens
    messages = relationship("Message", back_populates="connection")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("connections.id"))
    phone_dest = Column(String)  # Numero de destino
    content = Column(String)     # Texto da mensagem
    status = Column(String, default="pending") # pending, sent, error
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento reverso
    connection = relationship("Connection", back_populates="messages")
