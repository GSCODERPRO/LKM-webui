import time
from typing import Optional
from open_webui.internal.db import Base, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, Float, BigInteger, UniqueConstraint

class ModelPricing(Base):
    __tablename__ = 'model_pricing'
    id = Column(Integer, primary_key=True)
    model_id = Column(String, nullable=False, index=True, unique=True)
    auto_pricing = Column(Float, nullable=True)
    manual_price = Column(Float, nullable=True)
    source = Column(String, nullable=True)
    updated_at = Column(BigInteger, nullable=False)

class ModelPricingModel(BaseModel):
    id: int
    model_id: str
    auto_pricing: Optional[float] = None
    manual_price: Optional[float] = None
    source: Optional[str] = None
    updated_at: int
    model_config = ConfigDict(from_attributes=True)

class ModelPricingTable:
    def get_by_model_id(self, model_id: str) -> Optional[ModelPricingModel]:
        with get_db() as db:
            result = db.query(ModelPricing).filter_by(model_id=model_id).first()
            return ModelPricingModel.model_validate(result) if result else None
    def get_all(self) -> list[ModelPricingModel]:
        with get_db() as db:
            results = db.query(ModelPricing).all()
            return [ModelPricingModel.model_validate(r) for r in results]
    def upsert(self, model_id: str, auto_pricing: Optional[float], manual_price: Optional[float], source: Optional[str]) -> ModelPricingModel:
        with get_db() as db:
            now = int(time.time())
            obj = db.query(ModelPricing).filter_by(model_id=model_id).first()
            if obj:
                setattr(obj, 'auto_pricing', auto_pricing)
                setattr(obj, 'manual_price', manual_price)
                setattr(obj, 'source', source)
                setattr(obj, 'updated_at', now)
            else:
                obj = ModelPricing(
                    model_id=model_id,
                    auto_pricing=auto_pricing,
                    manual_price=manual_price,
                    source=source,
                    updated_at=now,
                )
                db.add(obj)
            db.commit()
            db.refresh(obj)
            return ModelPricingModel.model_validate(obj)

ModelPricings = ModelPricingTable() 