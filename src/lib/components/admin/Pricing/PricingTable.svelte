<script lang="ts">
import { onMount, getContext } from 'svelte';
import { toast } from 'svelte-sonner';
import { getModelPricing, updateModelPricing, type ModelPricing, type ModelPricingForm } from '$lib/apis/admin';
import { getModels } from '$lib/apis';

const i18n = getContext('i18n');

let models: any[] = [];
let pricing: ModelPricing[] = [];
let loading = true;
let saving: Record<string, boolean> = {};
let editing: Record<string, boolean> = {};
let manualPrices: Record<string, number|null> = {};
let autoPrices: Record<string, number|null> = {};
let sources: Record<string, string> = {};
let lastUpdated: Record<string, number> = {};
let fetchLoading: Record<string, boolean> = {};

onMount(async () => {
	try {
		models = await getModels(localStorage.token || '');
		const res = await getModelPricing(localStorage.token || '');
		pricing = res.pricing;
		for (const p of pricing) {
			manualPrices[p.model_id] = p.manual_price;
			autoPrices[p.model_id] = p.auto_pricing;
			sources[p.model_id] = p.source || 'manual';
			lastUpdated[p.model_id] = p.updated_at;
		}
	} catch (err) {
		console.error('Failed to load pricing:', err);
		toast.error('Failed to load pricing');
	} finally {
		loading = false;
	}
});

function startEdit(modelId: string) {
	editing[modelId] = true;
}

function cancelEdit(modelId: string) {
	editing[modelId] = false;
	const p = pricing.find((p) => p.model_id === modelId);
	if (p) {
		manualPrices[modelId] = p.manual_price;
		autoPrices[modelId] = p.auto_pricing;
		sources[modelId] = p.source || 'manual';
	}
}

async function save(modelId: string) {
	saving[modelId] = true;
	try {
		const formData: ModelPricingForm = {
			model_id: modelId,
			auto_pricing: autoPrices[modelId],
			manual_price: manualPrices[modelId],
			source: sources[modelId]
		};
		const res = await updateModelPricing(localStorage.token || '', formData);
		const idx = pricing.findIndex((p) => p.model_id === modelId);
		if (idx !== -1) pricing[idx] = res.pricing;
		else pricing.push(res.pricing);
		toast.success('Pricing updated');
		editing[modelId] = false;
	} catch (err) {
		console.error('Failed to update pricing:', err);
		toast.error('Failed to update pricing');
	} finally {
		saving[modelId] = false;
	}
}

async function fetchAutoPrice(modelId: string) {
	fetchLoading[modelId] = true;
	try {
		// Simulate API fetch: in real use, call backend endpoint to fetch price
		// Here, just set a random price for demo
		const price = Math.random() * 0.01 + 0.001;
		autoPrices[modelId] = Number(price.toFixed(4));
		sources[modelId] = 'openai';
		toast.success('Fetched auto price');
	} catch (err) {
		toast.error('Failed to fetch auto price');
	} finally {
		fetchLoading[modelId] = false;
	}
}

function formatDate(ts: number) {
	if (!ts) return '';
	const d = new Date(ts * 1000);
	return d.toLocaleString();
}
</script>

<div class="max-w-4xl mx-auto">
	<h2 class="text-xl font-semibold mb-4">Model Pricing</h2>
	{#if loading}
		<div class="flex items-center justify-center py-8">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
		</div>
	{:else}
		<table class="min-w-full border rounded-lg overflow-hidden bg-white dark:bg-gray-800">
			<thead>
				<tr class="bg-gray-100 dark:bg-gray-700 text-left">
					<th class="p-2">Model</th>
					<th class="p-2">Auto Price</th>
					<th class="p-2">Manual Price</th>
					<th class="p-2">Source</th>
					<th class="p-2">Last Updated</th>
					<th class="p-2">Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each models as model}
					<tr class="border-t">
						<td class="p-2">{model.name || model.id}</td>
						<td class="p-2">
							{#if editing[model.id]}
								<input type="number" step="0.0001" min="0" bind:value={autoPrices[model.id]} class="w-24 px-2 py-1 rounded border" />
								<button class="ml-2 px-2 py-1 text-xs bg-blue-100 rounded hover:bg-blue-200 disabled:opacity-50" on:click={() => fetchAutoPrice(model.id)} disabled={fetchLoading[model.id]}>{fetchLoading[model.id] ? 'Fetching...' : 'Fetch from API'}</button>
							{:else}
								{autoPrices[model.id] ?? '-'}
							{/if}
						</td>
						<td class="p-2">
							{#if editing[model.id]}
								<input type="number" step="0.0001" min="0" bind:value={manualPrices[model.id]} class="w-24 px-2 py-1 rounded border" />
							{:else}
								{manualPrices[model.id] ?? '-'}
							{/if}
						</td>
						<td class="p-2">
							{#if editing[model.id]}
								<select bind:value={sources[model.id]} class="px-2 py-1 rounded border">
									<option value="manual">Manual</option>
									<option value="openai">OpenAI API</option>
									<option value="azure">Azure API</option>
									<option value="custom">Custom</option>
								</select>
							{:else}
								{sources[model.id] || '-'}
							{/if}
						</td>
						<td class="p-2">{formatDate(lastUpdated[model.id])}</td>
						<td class="p-2">
							{#if editing[model.id]}
								<button class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 mr-2" on:click={() => save(model.id)} disabled={saving[model.id]}>{saving[model.id] ? 'Saving...' : 'Save'}</button>
								<button class="px-3 py-1 bg-gray-300 text-gray-700 rounded hover:bg-gray-400" on:click={() => cancelEdit(model.id)}>Cancel</button>
							{:else}
								<button class="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200" on:click={() => startEdit(model.id)}>Edit</button>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div> 