<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { user } from '$lib/stores';
	import { getUsageReport, type UsageReport } from '$lib/apis/admin';

	const i18n = getContext('i18n');

	let report: UsageReport | null = null;
	let loading = true;
	let error = '';

	// Default to current month
	let startDate = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
	let endDate = new Date().toISOString().split('T')[0];

	onMount(async () => {
		await loadReport();
	});

	async function loadReport() {
		loading = true;
		try {
			report = await getUsageReport($user?.token || '', startDate, endDate);
		} catch (err) {
			console.error('Failed to load usage report:', err);
			error = 'Failed to load usage report';
			toast.error('Failed to load usage report');
		} finally {
			loading = false;
		}
	}

	function formatNumber(num: number): string {
		return new Intl.NumberFormat().format(num);
	}

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(amount);
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString();
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-xl font-semibold">Usage Overview</h2>
		<div class="flex items-center gap-4">
			<div class="flex items-center gap-2">
				<label for="startDate" class="text-sm font-medium">Start Date:</label>
				<input
					id="startDate"
					type="date"
					bind:value={startDate}
					class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-700 dark:text-white"
				/>
			</div>
			<div class="flex items-center gap-2">
				<label for="endDate" class="text-sm font-medium">End Date:</label>
				<input
					id="endDate"
					type="date"
					bind:value={endDate}
					class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-700 dark:text-white"
				/>
			</div>
			<button
				on:click={loadReport}
				class="px-3 py-1.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition text-sm"
			>
				Update
			</button>
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-8">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
		</div>
	{:else if error}
		<div class="text-red-500 text-center py-8">{error}</div>
	{:else if report}
		<!-- Summary Cards -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
				<div class="flex items-center">
					<div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
						<svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
						</svg>
					</div>
					<div class="ml-4">
						<p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Tokens</p>
						<p class="text-2xl font-semibold text-gray-900 dark:text-white">{formatNumber(report.total_tokens)}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
				<div class="flex items-center">
					<div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
						<svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
						</svg>
					</div>
					<div class="ml-4">
						<p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Cost</p>
						<p class="text-2xl font-semibold text-gray-900 dark:text-white">{formatCurrency(report.total_cost)}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
				<div class="flex items-center">
					<div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
						<svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
						</svg>
					</div>
					<div class="ml-4">
						<p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Requests</p>
						<p class="text-2xl font-semibold text-gray-900 dark:text-white">{formatNumber(report.total_requests)}</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Date Range Info -->
		<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
			<p class="text-sm text-gray-600 dark:text-gray-300">
				Showing data from <span class="font-medium">{formatDate(startDate)}</span> to <span class="font-medium">{formatDate(endDate)}</span>
			</p>
		</div>

		<!-- Recent Activity -->
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow">
			<div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
				<h3 class="text-lg font-medium text-gray-900 dark:text-white">Recent Activity</h3>
			</div>
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
					<thead class="bg-gray-50 dark:bg-gray-700">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								User
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								Model
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								Tokens
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								Cost
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								Date
							</th>
						</tr>
					</thead>
					<tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
						{#each report.records.slice(0, 10) as record}
							<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
									{record.user_id}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{record.model}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{formatNumber(record.tokens_prompt + record.tokens_completion)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{formatCurrency(record.cost)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{new Date(record.timestamp * 1000).toLocaleDateString()}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div> 