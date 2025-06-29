<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { user } from '$lib/stores';
	import { getUsageReport, type UsageReport, type UsageRecord } from '$lib/apis/admin';

	const i18n = getContext('i18n');

	let report: UsageReport | null = null;
	let loading = true;
	let error = '';

	// Filters
	let startDate = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
	let endDate = new Date().toISOString().split('T')[0];
	let selectedUserId = '';
	let selectedModel = '';
	let page = 1;
	let pageSize = 50;

	// Available filters
	let users: string[] = [];
	let models: string[] = [];

	onMount(async () => {
		await loadReport();
	});

	async function loadReport() {
		loading = true;
		try {
			report = await getUsageReport(
				$user?.token || '', 
				startDate, 
				endDate, 
				selectedUserId || undefined, 
				selectedModel || undefined
			);

			// Extract unique users and models for filters
			if (report) {
				users = [...new Set(report.records.map(r => r.user_id))].sort();
				models = [...new Set(report.records.map(r => r.model))].sort();
			}
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

	function formatDate(timestamp: number): string {
		return new Date(timestamp * 1000).toLocaleDateString() + ' ' + 
			   new Date(timestamp * 1000).toLocaleTimeString();
	}

	function clearFilters() {
		startDate = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
		endDate = new Date().toISOString().split('T')[0];
		selectedUserId = '';
		selectedModel = '';
		page = 1;
		loadReport();
	}

	function getPaginatedRecords(): UsageRecord[] {
		if (!report) return [];
		const start = (page - 1) * pageSize;
		const end = start + pageSize;
		return report.records.slice(start, end);
	}

	function getTotalPages(): number {
		if (!report) return 0;
		return Math.ceil(report.records.length / pageSize);
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-xl font-semibold">Detailed Usage Reports</h2>
		<button
			on:click={loadReport}
			class="px-3 py-1.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition text-sm"
		>
			Refresh
		</button>
	</div>

	<!-- Filters -->
	<div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
		<h3 class="text-lg font-medium mb-4">Filters</h3>
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			<div>
				<label for="filterStartDate" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
					Start Date
				</label>
				<input
					id="filterStartDate"
					type="date"
					bind:value={startDate}
					class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-700 dark:text-white"
				/>
			</div>
			<div>
				<label for="filterEndDate" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
					End Date
				</label>
				<input
					id="filterEndDate"
					type="date"
					bind:value={endDate}
					class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-700 dark:text-white"
				/>
			</div>
			<div>
				<label for="filterUser" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
					User
				</label>
				<select
					id="filterUser"
					bind:value={selectedUserId}
					class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-700 dark:text-white"
				>
					<option value="">All Users</option>
					{#each users as user}
						<option value={user}>{user}</option>
					{/each}
				</select>
			</div>
			<div>
				<label for="filterModel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
					Model
				</label>
				<select
					id="filterModel"
					bind:value={selectedModel}
					class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-700 dark:text-white"
				>
					<option value="">All Models</option>
					{#each models as model}
						<option value={model}>{model}</option>
					{/each}
				</select>
			</div>
		</div>
		<div class="flex gap-3 mt-4">
			<button
				on:click={loadReport}
				class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
			>
				Apply Filters
			</button>
			<button
				on:click={clearFilters}
				class="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500 transition"
			>
				Clear Filters
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
		<!-- Summary -->
		<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
				<div>
					<p class="text-sm text-gray-600 dark:text-gray-300">Total Records</p>
					<p class="text-lg font-semibold text-gray-900 dark:text-white">{formatNumber(report.records.length)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600 dark:text-gray-300">Total Tokens</p>
					<p class="text-lg font-semibold text-gray-900 dark:text-white">{formatNumber(report.total_tokens)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600 dark:text-gray-300">Total Cost</p>
					<p class="text-lg font-semibold text-gray-900 dark:text-white">{formatCurrency(report.total_cost)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600 dark:text-gray-300">Total Requests</p>
					<p class="text-lg font-semibold text-gray-900 dark:text-white">{formatNumber(report.total_requests)}</p>
				</div>
			</div>
		</div>

		<!-- Records Table -->
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
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
								Prompt Tokens
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								Completion Tokens
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								Total Tokens
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
						{#each getPaginatedRecords() as record}
							<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
									{record.user_id}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{record.model}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{formatNumber(record.tokens_prompt)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{formatNumber(record.tokens_completion)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{formatNumber(record.tokens_prompt + record.tokens_completion)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{formatCurrency(record.cost)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{formatDate(record.timestamp)}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<!-- Pagination -->
			{#if getTotalPages() > 1}
				<div class="bg-white dark:bg-gray-800 px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
					<div class="flex-1 flex justify-between sm:hidden">
						<button
							on:click={() => page = Math.max(1, page - 1)}
							disabled={page === 1}
							class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Previous
						</button>
						<button
							on:click={() => page = Math.min(getTotalPages(), page + 1)}
							disabled={page === getTotalPages()}
							class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Next
						</button>
					</div>
					<div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
						<div>
							<p class="text-sm text-gray-700 dark:text-gray-300">
								Showing <span class="font-medium">{((page - 1) * pageSize) + 1}</span> to <span class="font-medium">{Math.min(page * pageSize, report.records.length)}</span> of <span class="font-medium">{report.records.length}</span> results
							</p>
						</div>
						<div>
							<nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
								<button
									on:click={() => page = Math.max(1, page - 1)}
									disabled={page === 1}
									class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
								>
									Previous
								</button>
								{#each Array.from({length: getTotalPages()}, (_, i) => i + 1) as pageNum}
									<button
										on:click={() => page = pageNum}
										class="relative inline-flex items-center px-4 py-2 border text-sm font-medium {pageNum === page ? 'z-10 bg-blue-50 border-blue-500 text-blue-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'}"
									>
										{pageNum}
									</button>
								{/each}
								<button
									on:click={() => page = Math.min(getTotalPages(), page + 1)}
									disabled={page === getTotalPages()}
									class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
								>
									Next
								</button>
							</nav>
						</div>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div> 