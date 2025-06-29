<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { user } from '$lib/stores';
	import { updateModelPricing, type ModelPricingForm } from '$lib/apis/admin';
	import { getModels } from '$lib/apis';

	const i18n = getContext('i18n');

	let models: any[] = [];
	let selectedModel = '';
	let autoPricing: number | null = null;
	let manualPrice: number | null = null;
	let source = 'manual';
	let loading = false;
	let modelsLoading = true;

	onMount(async () => {
		try {
			models = await getModels($user?.token || '');
		} catch (err) {
			console.error('Failed to load models:', err);
			toast.error('Failed to load models');
		} finally {
			modelsLoading = false;
		}
	});

	async function handleSubmit() {
		if (!selectedModel) {
			toast.error('Please select a model');
			return;
		}

		if (autoPricing === null && manualPrice === null) {
			toast.error('Please provide either auto pricing or manual price');
			return;
		}

		loading = true;
		try {
			const formData: ModelPricingForm = {
				model_id: selectedModel,
				auto_pricing: autoPricing,
				manual_price: manualPrice,
				source: source
			};

			await updateModelPricing($user?.token || '', formData);
			toast.success('Pricing updated successfully');
			
			// Reset form
			selectedModel = '';
			autoPricing = null;
			manualPrice = null;
			source = 'manual';
		} catch (err) {
			console.error('Failed to update pricing:', err);
			toast.error('Failed to update pricing');
		} finally {
			loading = false;
		}
	}

	function resetForm() {
		selectedModel = '';
		autoPricing = null;
		manualPrice = null;
		source = 'manual';
	}
</script>

<div class="max-w-2xl mx-auto space-y-6">
	<div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
		<h2 class="text-xl font-semibold mb-6">Manage Model Pricing</h2>

		{#if modelsLoading}
			<div class="flex items-center justify-center py-8">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
			</div>
		{:else}
			<form on:submit|preventDefault={handleSubmit} class="space-y-4">
				<div>
					<label for="model" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						Model
					</label>
					<select
						id="model"
						bind:value={selectedModel}
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
						required
					>
						<option value="">Select a model</option>
						{#each models as model}
							<option value={model.id}>{model.name || model.id}</option>
						{/each}
					</select>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="autoPricing" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							Auto Pricing (per 1K tokens)
						</label>
						<input
							id="autoPricing"
							type="number"
							step="0.0001"
							min="0"
							bind:value={autoPricing}
							placeholder="0.002"
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
						/>
						<p class="text-xs text-gray-500 mt-1">Leave empty to use manual price</p>
					</div>

					<div>
						<label for="manualPrice" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							Manual Price (per 1K tokens)
						</label>
						<input
							id="manualPrice"
							type="number"
							step="0.0001"
							min="0"
							bind:value={manualPrice}
							placeholder="0.003"
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
						/>
						<p class="text-xs text-gray-500 mt-1">Leave empty to use auto pricing</p>
					</div>
				</div>

				<div>
					<label for="source" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						Source
					</label>
					<select
						id="source"
						bind:value={source}
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
					>
						<option value="manual">Manual</option>
						<option value="openai">OpenAI API</option>
						<option value="azure">Azure API</option>
						<option value="custom">Custom</option>
					</select>
				</div>

				<div class="flex gap-3 pt-4">
					<button
						type="submit"
						disabled={loading}
						class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
					>
						{loading ? 'Updating...' : 'Update Pricing'}
					</button>
					<button
						type="button"
						on:click={resetForm}
						class="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500 transition"
					>
						Reset
					</button>
				</div>
			</form>
		{/if}
	</div>

	<div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
		<h3 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">Pricing Information</h3>
		<ul class="text-sm text-blue-700 dark:text-blue-300 space-y-1">
			<li>• Auto pricing will be fetched from the model provider's API</li>
			<li>• Manual pricing allows you to override the auto-fetched prices</li>
			<li>• If both are set, manual pricing takes precedence</li>
			<li>• Prices are stored per 1K tokens for consistency</li>
		</ul>
	</div>
</div> 