<script>
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import toast from 'svelte-french-toast';

	let email = '';
	let password = '';
	let loading = false;

	async function handleLogin() {
		try {
			loading = true;
			const { error } = await supabase.auth.signInWithPassword({ email, password });
			if (error) throw error;
			toast.success('Successfully logged in!');
			goto('/app');
		} catch (error) {
			toast.error(error.message);
		} finally {
			loading = false;
		}
	}

	async function handleMagicLink() {
		try {
			loading = true;
			if (!email) {
				toast.error('Please enter your email first.');
				return;
			}
			const { error } = await supabase.auth.signInWithOtp({
				email,
				options: {
					emailRedirectTo: window.location.origin + '/app'
				}
			});
			if (error) throw error;
			toast.success('Magic link sent! Check your email.');
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
			<h2
				class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary"
			>
				Welcome Back
			</h2>
			<p class="opacity-60">Sign in to continue transcribing</p>
		</div>

		<div class="form-control w-full">
			<label class="label" for="email">
				<span class="label-text">Email</span>
			</label>
			<input
				id="email"
				type="email"
				placeholder="email@example.com"
				bind:value={email}
				class="input input-bordered w-full"
			/>
		</div>

		<div class="form-control w-full mt-4">
			<label class="label" for="password">
				<span class="label-text">Password</span>
			</label>
			<input
				id="password"
				type="password"
				placeholder="••••••••"
				bind:value={password}
				class="input input-bordered w-full"
			/>
			<label class="label" for="forgot">
				<a id="forgot" href="/auth/forgot-password" class="label-text-alt link link-primary"
					>Forgot password?</a
				>
			</label>
		</div>

		<div class="form-control mt-6 gap-3">
			<button class="btn btn-primary w-full" on:click={handleLogin} disabled={loading}>
				{#if loading}<span class="loading loading-spinner loading-sm" />{/if}
				Sign In
			</button>
			<div class="divider text-xs opacity-50 my-1">OR</div>
			<button
				class="btn btn-ghost border border-base-content/10 w-full hover:bg-base-200"
				on:click={handleMagicLink}
				disabled={loading}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-5 h-5 mr-2"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M13 10V3L4 14h7v7l9-11h-7z"
					/>
				</svg>
				Sign in with Magic Link
			</button>
		</div>

		<div class="text-center mt-6 text-sm opacity-80">
			Don't have an account? <a href="/auth/register" class="link link-primary font-bold">Sign up</a
			>
		</div>
	</div>
</div>
