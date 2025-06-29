import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from open_webui.utils.auth import get_admin_user
from open_webui.models.users import UserModel
from open_webui.models.model_pricing import ModelPricings, ModelPricingModel
from open_webui.models.usage_log import UsageLogs, UsageLogModel
from open_webui.utils.pricing import pricing_service
from open_webui.utils.usage_logger import usage_logger
from open_webui.env import SRC_LOG_LEVELS
import traceback

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("ADMIN", "INFO"))

router = APIRouter()

class ModelPricingForm(BaseModel):
    model_id: str
    auto_pricing: Optional[float] = None
    manual_price: Optional[float] = None
    source: str = "manual"

class UsageReportResponse(BaseModel):
    total_tokens: int
    total_cost: float
    total_requests: int
    records: List[dict]

@router.get("/models/pricing")
async def get_model_pricing(user: UserModel = Depends(get_admin_user)):
    """Get all model pricing information"""
    try:
        pricing_records = ModelPricings.get_all()
        return {"pricing": [r.model_dump() for r in pricing_records]}
    except Exception as e:
        log.error(f"Failed to get model pricing: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model pricing")

@router.post("/models/pricing")
async def update_model_pricing(
    form_data: ModelPricingForm,
    user: UserModel = Depends(get_admin_user)
):
    """Update pricing for a model"""
    try:
        pricing_record = pricing_service.update_model_pricing(
            model_id=form_data.model_id,
            auto_pricing=form_data.auto_pricing,
            manual_price=form_data.manual_price,
            source=form_data.source
        )
        return {"success": True, "pricing": pricing_record}
    except Exception as e:
        log.error(f"Failed to update model pricing: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to update model pricing: {e}")

@router.get("/reports/usage")
async def get_usage_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    model: Optional[str] = Query(None, description="Filter by model"),
    user: UserModel = Depends(get_admin_user)
):
    """Get usage reports with optional filtering"""
    try:
        # Convert dates to timestamps if provided
        start_timestamp = None
        end_timestamp = None
        
        if start_date:
            import time
            from datetime import datetime
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        
        if end_date:
            import time
            from datetime import datetime
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        
        # Get all usage records
        all_records = []
        if user_id:
            # Get records for specific user
            user_summary = usage_logger.get_user_usage_summary(
                user_id, start_timestamp, end_timestamp
            )
            if user_summary:
                all_records = user_summary["records"]
        else:
            # Get all records (this would need pagination for large datasets)
            # For now, return empty list
            all_records = []
        
        # Filter by model if specified
        if model:
            all_records = [r for r in all_records if r.model == model]
        
        # Calculate totals
        total_tokens = sum(r.tokens_prompt + r.tokens_completion for r in all_records)
        total_cost = sum(r.cost for r in all_records)
        total_requests = len(all_records)
        
        return UsageReportResponse(
            total_tokens=total_tokens,
            total_cost=total_cost,
            total_requests=total_requests,
            records=[r.model_dump() for r in all_records]
        )
        
    except Exception as e:
        log.error(f"Failed to get usage report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage report")

@router.get("/reports/users/{user_id}")
async def get_user_usage_report(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user: UserModel = Depends(get_admin_user)
):
    """Get usage report for a specific user"""
    try:
        # Convert dates to timestamps if provided
        start_timestamp = None
        end_timestamp = None
        
        if start_date:
            import time
            from datetime import datetime
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        
        if end_date:
            import time
            from datetime import datetime
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        
        user_summary = usage_logger.get_user_usage_summary(
            user_id, start_timestamp, end_timestamp
        )
        
        if user_summary is None:
            raise HTTPException(status_code=404, detail="User not found or no usage data")
        
        return UsageReportResponse(
            total_tokens=user_summary["total_tokens"],
            total_cost=user_summary["total_cost"],
            total_requests=user_summary["total_requests"],
            records=[r.model_dump() for r in user_summary["records"]]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to get user usage report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user usage report") 