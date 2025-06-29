<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	import Pricing from '$lib/components/admin/Pricing.svelte';

	onMount(() => {
		goto('/admin/pricing/overview');
	});
</script>

<Pricing /> 