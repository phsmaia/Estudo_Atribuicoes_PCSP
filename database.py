import os
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import enum

def get_br_time():
    return datetime.now(timezone(timedelta(hours=-3)))

Base = declarative_base()

class CommentStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Interaction(Base):
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    section_name = Column(String(255), nullable=False)
    user_hash = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=get_br_time)

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    section_name = Column(String(255), nullable=False)
    user_hash = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=True)
    text = Column(Text, nullable=False)
    status = Column(Enum(CommentStatus), default=CommentStatus.PENDING)
    language = Column(String(10), default="PT-BR")
    timestamp = Column(DateTime, default=get_br_time)

class AnalyticsSession(Base):
    __tablename__ = 'analytics_sessions'
    
    session_id = Column(String(255), primary_key=True)
    user_hash = Column(String(255), nullable=False)
    start_time = Column(DateTime, default=get_br_time)
    last_activity = Column(DateTime, default=get_br_time)
    os_name = Column(String(100), default="Unknown")
    browser_name = Column(String(100), default="Unknown")
    inferred_persona = Column(String(100), default="Desconhecido")

class AnalyticsEvent(Base):
    __tablename__ = 'analytics_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=get_br_time)
    event_type = Column(String(100), nullable=False)
    event_data = Column(Text, nullable=True) # JSON payload
# Configuração do SQLite no mesmo diretório do projeto
DB_PATH = os.path.join(os.path.dirname(__file__), "app_data.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Cria as tabelas se elas não existirem
Base.metadata.create_all(engine)

from sqlalchemy import text
try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE comments ADD COLUMN language VARCHAR(10) DEFAULT 'PT-BR'"))
except Exception:
    pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Retorna uma sessão do banco de dados SQLAlchemy."""
    return SessionLocal()
