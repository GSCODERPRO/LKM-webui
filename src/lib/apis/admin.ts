import { WEBUI_BASE_URL } from '$lib/constants';

// Model Pricing Management
export interface ModelPricing {
	id: number;
	model_id: string;
	auto_pricing: number | null;
	manual_price: number | null;
	source: string | null;
	updated_at: number;
}

export interface ModelPricingForm {
	model_id: string;
	auto_pricing?: number | null;
	manual_price?: number | null;
	source?: string;
}

export const getModelPricing = async (token: string): Promise<{ pricing: ModelPricing[] }> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/admin/models/pricing`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	});

	if (!res.ok) {
		throw await res.json();
	}

	return res.json();
};

export const updateModelPricing = async (token: string, formData: ModelPricingForm): Promise<{ success: boolean; pricing: ModelPricing }> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/admin/models/pricing`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify(formData)
	});

	if (!res.ok) {
		throw await res.json();
	}

	return res.json();
};

// Usage Reports
export interface UsageReport {
	total_tokens: number;
	total_cost: number;
	total_requests: number;
	records: UsageRecord[];
}

export interface UsageRecord {
	id: number;
	user_id: string;
	model: string;
	tokens_prompt: number;
	tokens_completion: number;
	cost: number;
	timestamp: number;
	conversation_id: string | null;
}

export const getUsageReport = async (
	token: string,
	startDate?: string,
	endDate?: string,
	userId?: string,
	model?: string
): Promise<UsageReport> => {
	const params = new URLSearchParams();
	if (startDate) params.append('startDate', startDate);
	if (endDate) params.append('endDate', endDate);
	if (userId) params.append('user_id', userId);
	if (model) params.append('model', model);

	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/admin/reports/usage?${params}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	});

	if (!res.ok) {
		throw await res.json();
	}

	return res.json();
};

export const getUserUsageReport = async (
	token: string,
	userId: string,
	startDate?: string,
	endDate?: string
): Promise<UsageReport> => {
	const params = new URLSearchParams();
	if (startDate) params.append('startDate', startDate);
	if (endDate) params.append('endDate', endDate);

	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/admin/reports/users/${userId}?${params}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	});

	if (!res.ok) {
		throw await res.json();
	}

	return res.json();
}; 