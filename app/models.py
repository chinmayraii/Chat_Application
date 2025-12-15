from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
import random
import time

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    identity_stability = Column(String, default="stable")

    def apply_identity_drift(self):
        drift_factor = random.random()
        if drift_factor < 0.05:
            self.identity_stability = "unstable"
        elif drift_factor < 0.15:
            self.identity_stability = "fluctuating"
        else:
            self.identity_stability = "stable"

