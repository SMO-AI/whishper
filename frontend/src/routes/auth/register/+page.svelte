<script>
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import toast from 'svelte-french-toast';

	let email = '';
	let password = '';
	let confirmPassword = '';
	let loading = false;

	async function handleRegister() {
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
			const { error } = await supabase.auth.signUp({
				email,
				password,
				options: {
					data: {
						app: 'whishper'
					},
					emailRedirectTo: window.location.origin + '/app'
				}
			});
			if (error) throw error;
			toast.success('Registration successful! Please check your email.');
			goto('/auth/login');
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
				Create Account
			</h2>
			<p class="opacity-60">Start your journey with Whishper</p>
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
		</div>

		<div class="form-control w-full mt-4">
			<label class="label" for="confirm_password">
				<span class="label-text">Confirm Password</span>
			</label>
			<input
				id="confirm_password"
				type="password"
				placeholder="••••••••"
				bind:value={confirmPassword}
				class="input input-bordered w-full"
			/>
		</div>

		<div class="form-control mt-8">
			<button class="btn btn-primary w-full" on:click={handleRegister} disabled={loading}>
				{#if loading}<span class="loading loading-spinner loading-sm" />{/if}
				Create Account
			</button>
		</div>

		<div class="text-center mt-6 text-sm opacity-80">
			Already have an account? <a href="/auth/login" class="link link-primary font-bold">Sign in</a>
		</div>
	</div>
</div>
