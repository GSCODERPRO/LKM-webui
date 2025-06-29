import logging
import aiohttp
from typing import Optional, Dict, Any
from open_webui.models.model_pricing import ModelPricings
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("PRICING", "INFO"))

# OpenAI pricing data (as of 2024) - this could be fetched dynamically
OPENAI_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
}

class PricingService:
    @staticmethod
    async def fetch_openai_pricing(api_key: str, base_url: str = "https://api.openai.com/v1") -> Dict[str, Any]:
        """Fetch pricing from OpenAI API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{base_url}/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                ) as response:
                    if response.status == 200:
                        models_data = await response.json()
                        pricing_data = {}
                        for model in models_data.get("data", []):
                            model_id = model.get("id")
                            if model_id in OPENAI_PRICING:
                                pricing_data[model_id] = OPENAI_PRICING[model_id]
                        return pricing_data
        except Exception as e:
            log.error(f"Failed to fetch OpenAI pricing: {e}")
        return {}

    @staticmethod
    def get_model_pricing(model_id: str) -> Optional[float]:
        """Get pricing for a specific model (input tokens per 1K)"""
        pricing_record = ModelPricings.get_by_model_id(model_id)
        if pricing_record:
            # Return manual price if set, otherwise auto pricing
            return pricing_record.manual_price or pricing_record.auto_pricing
        return None

    @staticmethod
    def calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a model usage"""
        pricing_record = ModelPricings.get_by_model_id(model_id)
        if not pricing_record:
            # Fallback to default pricing if not found
            if model_id in OPENAI_PRICING:
                input_cost = (input_tokens / 1000) * OPENAI_PRICING[model_id]["input"]
                output_cost = (output_tokens / 1000) * OPENAI_PRICING[model_id]["output"]
                return input_cost + output_cost
            return 0.0
        
        # Use manual price if set, otherwise auto pricing
        price_per_1k = pricing_record.manual_price or pricing_record.auto_pricing
        if price_per_1k is None:
            return 0.0
        
        # For simplicity, assume same price for input/output tokens
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * price_per_1k

    @staticmethod
    def update_model_pricing(model_id: str, auto_pricing: Optional[float] = None, 
                           manual_price: Optional[float] = None, source: str = "manual"):
        """Update pricing for a model"""
        return ModelPricings.upsert(model_id, auto_pricing, manual_price, source)

# Global pricing service instance
pricing_service = PricingService() 