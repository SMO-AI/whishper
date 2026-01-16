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

	async function handleGoogleLogin() {
		try {
			loading = true;
			const { error } = await supabase.auth.signInWithOAuth({
				provider: 'google',
				options: {
					redirectTo: window.location.origin + '/app'
				}
			});
			if (error) throw error;
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

		<div class="divider text-xs opacity-50 my-4">OR CONTINUE WITH</div>
		<button
			class="btn btn-outline w-full gap-2 hover:bg-base-200 transition-all duration-300"
			on:click={handleGoogleLogin}
			disabled={loading}
		>
			<svg class="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
				<path
					d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
					fill="#4285F4"
				/>
				<path
					d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
					fill="#34A853"
				/>
				<path
					d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
					fill="#FBBC05"
				/>
				<path
					d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
					fill="#EA4335"
				/>
			</svg>
			Google
		</button>
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

		<div class="text-center mt-6 text-sm opacity-80">
			Don't have an account? <a href="/auth/register" class="link link-primary font-bold">Sign up</a
			>
		</div>
	</div>
</div>
