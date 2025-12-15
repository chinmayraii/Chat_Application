from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "12345")
POSTGRES_DB = os.getenv("POSTGRES_DB", "chat_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "chat_messages")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

mongo_client = None
mongo_db = None

def get_mongo_client():
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return mongo_client

def get_mongo_db():
    global mongo_db
    if mongo_db is None:
        client = get_mongo_client()
        mongo_db = client[MONGODB_DB]
    return mongo_db

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        client = get_mongo_client()
        client.admin.command('ping')
    except ConnectionFailure:
        pass

