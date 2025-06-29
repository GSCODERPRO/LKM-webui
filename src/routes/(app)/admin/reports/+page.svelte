<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	import Reports from '$lib/components/admin/Reports.svelte';

	onMount(() => {
		goto('/admin/reports/overview');
	});
</script>

<Reports /> 