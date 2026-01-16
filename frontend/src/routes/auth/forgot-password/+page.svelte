<script>
	import { supabase } from '$lib/supabase';
	import toast from 'svelte-french-toast';

	let email = '';
	let loading = false;

	async function handleReset() {
		if (!email) {
			toast.error('Please enter your email');
			return;
		}
		try {
			loading = true;
			const { error } = await supabase.auth.resetPasswordForEmail(email, {
				redirectTo: window.location.origin + '/auth/update-password'
			});
			if (error) throw error;
			toast.success('Password reset instructions sent to your email.');
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
			<h2 class="text-2xl font-bold">Reset Password</h2>
			<p class="opacity-60 text-sm mt-2">
				Enter your email address and we'll send you a link to reset your password.
			</p>
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

		<div class="form-control mt-6">
			<button class="btn btn-primary w-full" on:click={handleReset} disabled={loading}>
				{#if loading}<span class="loading loading-spinner loading-sm" />{/if}
				Send Reset Link
			</button>
		</div>

		<div class="text-center mt-6 text-sm">
			<a href="/auth/login" class="link link-hover flex items-center justify-center gap-2">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 19l-7-7m0 0l7-7m-7 7h18"
					/>
				</svg>
				Back to Sign In
			</a>
		</div>
	</div>
</div>
