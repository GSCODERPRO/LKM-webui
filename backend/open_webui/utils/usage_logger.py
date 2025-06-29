import logging
from typing import Optional
from open_webui.models.usage_log import UsageLogs
from open_webui.utils.pricing import pricing_service
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("USAGE_LOGGER", "INFO"))

class UsageLogger:
    @staticmethod
    def log_usage(user_id: str, model: str, input_tokens: int, output_tokens: int, 
                 conversation_id: Optional[str] = None) -> bool:
        """Log usage and calculate cost"""
        try:
            # Calculate cost using pricing service
            cost = pricing_service.calculate_cost(model, input_tokens, output_tokens)
            
            # Log the usage
            usage_record = UsageLogs.log_usage(
                user_id=user_id,
                model=model,
                tokens_prompt=input_tokens,
                tokens_completion=output_tokens,
                cost=cost,
                conversation_id=conversation_id
            )
            
            log.info(f"Logged usage: user={user_id}, model={model}, "
                    f"tokens={input_tokens}+{output_tokens}, cost=${cost:.4f}")
            return True
            
        except Exception as e:
            log.error(f"Failed to log usage: {e}")
            return False

    @staticmethod
    def get_user_usage_summary(user_id: str, start_timestamp: Optional[int] = None, 
                             end_timestamp: Optional[int] = None):
        """Get usage summary for a user"""
        try:
            usage_records = UsageLogs.get_by_user_id(user_id)
            
            # Filter by timestamp if provided
            if start_timestamp or end_timestamp:
                filtered_records = []
                for record in usage_records:
                    if start_timestamp and record.timestamp < start_timestamp:
                        continue
                    if end_timestamp and record.timestamp > end_timestamp:
                        continue
                    filtered_records.append(record)
                usage_records = filtered_records
            
            # Calculate summary
            total_tokens = sum(r.tokens_prompt + r.tokens_completion for r in usage_records)
            total_cost = sum(r.cost for r in usage_records)
            total_requests = len(usage_records)
            
            return {
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "total_requests": total_requests,
                "records": usage_records
            }
            
        except Exception as e:
            log.error(f"Failed to get user usage summary: {e}")
            return None

    @staticmethod
    def get_conversation_usage(conversation_id: str):
        """Get usage for a specific conversation"""
        try:
            return UsageLogs.get_by_conversation_id(conversation_id)
        except Exception as e:
            log.error(f"Failed to get conversation usage: {e}")
            return []

# Global usage logger instance
usage_logger = UsageLogger() 