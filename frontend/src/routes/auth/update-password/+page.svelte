<script>
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import toast from 'svelte-french-toast';
	import { onMount } from 'svelte';

	let password = '';
	let confirmPassword = '';
	let loading = false;

	onMount(async () => {
		const {
			data: { session }
		} = await supabase.auth.getSession();
		if (!session) {
			// In some flows, the session might be established by the URL fragment handled by Supabase client auto-detect.
			// We'll give it a moment or check if we have an error fragment.
		}
	});

	async function handleUpdate() {
		if (password !== confirmPassword) {
			toast.error("Passwords don't match");
			return;
		}
		if (password.length < 6) {
			toast.error('Password must be at least 6 characters');
			return;
		}

		try {
			loading = true;
			const { error } = await supabase.auth.updateUser({ password });
			if (error) throw error;
			toast.success('Password updated successfully!');
			goto('/app');
		} catch (error) {
			toast.error(error.message);
		} finally {
			loading = false;
		}
	}
</script>

<div class="card bg-base-100 shadow-2xl border border-base-200">
	<div class="card-body">
		<div class="text-center mb-6">
			<h2 class="text-2xl font-bold">Set New Password</h2>
			<p class="opacity-60 text-sm mt-2">Secure your account with a new password.</p>
		</div>

		<div class="form-control w-full">
			<label class="label" for="password">
				<span class="label-text">New Password</span>
			</label>
			<input
				id="password"
				type="password"
				placeholder="••••••••"
				bind:value={password}
				class="input input-bordered w-full"
			/>
		</div>

		<div class="form-control w-full mt-4">
			<label class="label" for="confirm_password">
				<span class="label-text">Confirm New Password</span>
			</label>
			<input
				id="confirm_password"
				type="password"
				placeholder="••••••••"
				bind:value={confirmPassword}
				class="input input-bordered w-full"
			/>
		</div>

		<div class="form-control mt-6">
			<button class="btn btn-primary w-full" on:click={handleUpdate} disabled={loading}>
				{#if loading}<span class="loading loading-spinner loading-sm" />{/if}
				Update Password
			</button>
		</div>
	</div>
</div>
