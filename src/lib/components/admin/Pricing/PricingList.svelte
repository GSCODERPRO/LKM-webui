<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { user } from '$lib/stores';
	import { getModelPricing, type ModelPricing } from '$lib/apis/admin';
	import { getModels } from '$lib/apis';

	const i18n = getContext('i18n');

	let pricing: ModelPricing[] = [];
	let models: any[] = [];
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			await loadData();
		} catch (err) {
			console.error('Failed to load pricing data:', err);
			error = 'Failed to load pricing data';
			toast.error('Failed to load pricing data');
		} finally {
			loading = false;
		}
	});

	async function loadData() {
		const [pricingResponse, modelsResponse] = await Promise.all([
			getModelPricing($user?.token || ''),
			getModels($user?.token || '')
		]);

		pricing = pricingResponse.pricing;
		models = modelsResponse;
	}

	function getModelName(modelId: string): string {
		const model = models.find(m => m.id === modelId);
		return model?.name || modelId;
	}

	function formatPrice(price: number | null): string {
		if (price === null) return 'N/A';
		return `$${(price / 1000).toFixed(4)}/1K tokens`;
	}

	function formatDate(timestamp: number): string {
		return new Date(timestamp * 1000).toLocaleDateString();
	}
</script>

<div class="space-y-4">
	<div class="flex items-center justify-between">
		<h2 class="text-xl font-semibold">Model Pricing Overview</h2>
		<button
			class="px-3 py-1.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
			on:click={loadData}
		>
			Refresh
		</button>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-8">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
		</div>
	{:else if error}
		<div class="text-red-500 text-center py-8">{error}</div>
	{:else if pricing.length === 0}
		<div class="text-center py-8 text-gray-500">
			No pricing data available. Add pricing information in the Manage tab.
		</div>
	{:else}
		<div class="overflow-x-auto">
			<table class="min-w-full bg-white dark:bg-gray-800 rounded-lg overflow-hidden">
				<thead class="bg-gray-50 dark:bg-gray-700">
					<tr>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
							Model
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
							Auto Pricing
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
							Manual Price
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
							Source
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
							Last Updated
						</th>
					</tr>
				</thead>
				<tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
					{#each pricing as item}
						<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
							<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
								{getModelName(item.model_id)}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
								{formatPrice(item.auto_pricing)}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
								{formatPrice(item.manual_price)}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
								{item.source || 'N/A'}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
								{formatDate(item.updated_at)}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div> 