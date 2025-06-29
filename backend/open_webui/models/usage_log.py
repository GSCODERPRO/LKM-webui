# Requires: pydantic
import time
from typing import Optional
from open_webui.internal.db import Base, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, Float, BigInteger

class UsageLog(Base):
    __tablename__ = 'usage_log'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False)
    tokens_prompt = Column(Integer, nullable=False)
    tokens_completion = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    conversation_id = Column(String, nullable=True, index=True)

class UsageLogModel(BaseModel):
    id: int
    user_id: str
    model: str
    tokens_prompt: int
    tokens_completion: int
    cost: float
    timestamp: int
    conversation_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class UsageLogTable:
    def log_usage(self, user_id: str, model: str, tokens_prompt: int, tokens_completion: int, cost: float, conversation_id: Optional[str] = None) -> UsageLogModel:
        with get_db() as db:
            now = int(time.time())
            obj = UsageLog(
                user_id=user_id,
                model=model,
                tokens_prompt=tokens_prompt,
                tokens_completion=tokens_completion,
                cost=cost,
                timestamp=now,
                conversation_id=conversation_id,
            )
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return UsageLogModel.model_validate(obj)
    def get_by_user_id(self, user_id: str):
        with get_db() as db:
            return db.query(UsageLog).filter_by(user_id=user_id).all()
    def get_by_conversation_id(self, conversation_id: str):
        with get_db() as db:
            return db.query(UsageLog).filter_by(conversation_id=conversation_id).all()

UsageLogs = UsageLogTable() 