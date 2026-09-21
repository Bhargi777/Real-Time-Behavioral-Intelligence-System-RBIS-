from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

# SQLite for local dev, easily swap for PostgreSQL
DATABASE_URL = "sqlite:///./rbis.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

class BehaviorEvent(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True)
    event_type = Column(String)
    timestamp = Column(DateTime, default=utcnow)
    confidence = Column(Float)

class EngagementMetric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True)
    engagement_score = Column(Float)
    timestamp = Column(DateTime, default=utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database schema initialized.")
