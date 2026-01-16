<script>
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import toast, { Toaster } from 'svelte-french-toast';

	let loading = true;
	let isAdmin = false;

	onMount(async () => {
		const {
			data: { session }
		} = await supabase.auth.getSession();
		if (!session) {
			goto('/auth/login');
			return;
		}

		// Check Admin Status
		const { data: profile, error } = await supabase
			.from('whishper_profiles')
			.select('role')
			.eq('id', session.user.id)
			.single();

		if (error || profile?.role !== 'admin') {
			toast.error('Unauthorized access');
			goto('/app');
			return;
		}

		isAdmin = true;
		loading = false;
	});
</script>

<Toaster />

{#if loading}
	<div class="flex items-center justify-center min-h-screen">
		<span class="loading loading-spinner loading-lg" />
	</div>
{:else if isAdmin}
	<div class="min-h-screen bg-base-200">
		<div class="navbar bg-base-100 shadow px-6">
			<div class="flex-1">
				<a class="btn btn-ghost normal-case text-xl font-bold text-primary" href="/admin"
					>Scriptus Admin</a
				>
			</div>
			<div class="flex-none gap-4">
				<a href="/app" class="btn btn-ghost btn-sm">Back to App</a>
			</div>
		</div>

		<div class="p-8">
			<slot />
		</div>
	</div>
{/if}
