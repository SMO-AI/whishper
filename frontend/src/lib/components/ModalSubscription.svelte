<script>
	import { supabase } from '$lib/supabase';
	import toast from 'svelte-french-toast';
	import { onMount } from 'svelte';
	import { t } from '$lib/stores';

	export let show = false;
	let code = '';
	let loading = false;
	let status = 'loading'; // 'loading', 'active', 'passive'

	export function showModal() {
		document.getElementById('modal_subscription').showModal();
		checkStatus();
	}

	async function checkStatus() {
		const {
			data: { session }
		} = await supabase.auth.getSession();
		if (session) {
			const { data, error } = await supabase
				.from('whishper_profiles')
				.select('status')
				.eq('id', session.user.id)
				.single();

			if (data) {
				status = data.status || 'passive';
			}
		}
	}

	async function activate() {
		if (!code) return;
		loading = true;
		try {
			const { data, error } = await supabase.rpc('activate_subscription', { input_code: code });
			if (error) throw error;

			if (data.success) {
				toast.success(data.message);
				status = 'active';
				code = '';
			} else {
				toast.error(data.message);
			}
		} catch (e) {
			toast.error(e.message);
		} finally {
			loading = false;
		}
	}
</script>

<dialog id="modal_subscription" class="modal">
	<div class="modal-box">
		<form method="dialog">
			<button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
		</form>

		<h3 class="font-bold text-lg mb-4">{$t('sub_status')}</h3>

		{#if status === 'active'}
			<div class="alert alert-success">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="stroke-current shrink-0 h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
					/></svg
				>
				<span>{$t('sub_active')}</span>
			</div>
		{:else}
			<div class="alert alert-warning mb-4">
				<span>{$t('sub_passive')}</span>
			</div>
			<p class="mb-4 text-sm opacity-70">
				{$t('sub_demo_msg')}
			</p>

			<div class="form-control w-full">
				<label class="label">
					<span class="label-text">{$t('activation_code')}</span>
				</label>
				<input
					type="text"
					placeholder={$t('enter_code')}
					class="input input-bordered w-full"
					bind:value={code}
				/>
			</div>

			<div class="modal-action">
				<button class="btn btn-primary" on:click={activate} disabled={loading}>
					{#if loading}
						<span class="loading loading-spinner loading-xs" />
					{/if}
					{$t('activate')}
				</button>
			</div>
		{/if}
	</div>
</dialog>
