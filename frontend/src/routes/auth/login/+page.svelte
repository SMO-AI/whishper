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

<div class="card bg-base-100/80 backdrop-blur-xl shadow-2xl border border-white/10 overflow-hidden">
	<div class="card-body p-8">
		<div class="text-center mb-8">
			<div class="inline-block p-3 rounded-2xl bg-primary/10 mb-4">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-10 h-10 text-primary"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
					/>
				</svg>
			</div>
			<h2 class="text-3xl font-bold tracking-tight mb-2">Welcome Back</h2>
			<p class="opacity-60 text-sm">Enter your credentials to access your workspace</p>
		</div>

		<button
			class="btn btn-outline w-full gap-3 h-12 hover:bg-base-content/5 hover:border-base-content/20 transition-all font-medium normal-case text-base mb-6 relative overflow-hidden group"
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
			Continue with Google
		</button>

		<div class="relative mb-6">
			<div class="absolute inset-0 flex items-center">
				<div class="w-full border-t border-base-content/10" />
			</div>
			<div class="relative flex justify-center text-xs uppercase">
				<span class="bg-base-100 px-2 text-base-content/40 font-semibold tracking-wider"
					>Or email</span
				>
			</div>
		</div>

		<div class="space-y-4">
			<div class="form-control w-full">
				<label class="label" for="email">
					<span class="label-text font-medium">Email</span>
				</label>
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-5 w-5 opacity-40"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
							/>
						</svg>
					</div>
					<input
						id="email"
						type="email"
						placeholder="name@example.com"
						bind:value={email}
						class="input input-bordered w-full pl-10 bg-base-200/50 focus:bg-base-100 transition-colors"
					/>
				</div>
			</div>

			<div class="form-control w-full">
				<label class="label justify-between items-center" for="password">
					<span class="label-text font-medium">Password</span>
					<a
						href="/auth/forgot-password"
						class="label-text-alt link link-primary hover:no-underline opacity-80 hover:opacity-100"
						>Forgot password?</a
					>
				</label>
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-5 w-5 opacity-40"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							/>
						</svg>
					</div>
					<input
						id="password"
						type="password"
						placeholder="••••••••"
						bind:value={password}
						class="input input-bordered w-full pl-10 bg-base-200/50 focus:bg-base-100 transition-colors"
					/>
				</div>
			</div>

			<button
				class="btn btn-primary w-full shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all text-lg font-bold mt-2"
				on:click={handleLogin}
				disabled={loading}
			>
				{#if loading}<span class="loading loading-spinner loading-sm" />{/if}
				Sign In
			</button>

			<button
				class="btn btn-ghost btn-sm w-full font-normal opacity-70 hover:opacity-100 hover:bg-transparent"
				on:click={handleMagicLink}
				disabled={loading}
			>
				Sign in with <span class="text-primary font-medium ml-1">Magic Link</span>
			</button>
		</div>

		<div class="text-center mt-8 text-sm opacity-60">
			Don't have an account? <a
				href="/auth/register"
				class="link link-primary font-bold hover:no-underline">Create account</a
			>
		</div>
	</div>
</div>
