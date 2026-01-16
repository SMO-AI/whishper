<!-- SuccessTranscription.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { deleteTranscription } from '$lib/utils.js';
	import { fade } from 'svelte/transition';
	export let tr;

	const dispatch = createEventDispatcher();
	let download = () => {
		dispatch('download', tr);
	};
	let translate = () => {
		dispatch('translate', tr);
	};

	// Extract date from MongoDB ID
	$: date = tr.id
		? new Date(parseInt(tr.id.substring(0, 8), 16) * 1000).toLocaleString()
		: 'Recent';
	$: snippet = tr.result.text
		? tr.result.text.substring(0, 150) + (tr.result.text.length > 150 ? '...' : '')
		: 'No content';
	$: fileName = tr.fileName ? tr.fileName.split('_WHSHPR_')[1] : 'Unnamed';
	$: duration = tr.result.duration
		? new Date(Math.round(tr.result.duration) * 1000).toISOString().substr(11, 8)
		: '00:00:00';
	$: wordCount = tr.result.text
		? tr.result.text.split(/\s+/).filter((w) => w.length > 0).length
		: 0;
</script>

<div
	class="group relative bg-base-200/50 hover:bg-base-200 border border-base-300 hover:border-primary/30 rounded-2xl p-5 md:p-6 transition-all duration-300 shadow-sm hover:shadow-xl mt-4"
	in:fade
>
	<!-- Left glow effect on hover -->
	<div
		class="absolute inset-y-0 left-0 w-1 bg-primary scale-y-0 group-hover:scale-y-100 transition-transform duration-300 rounded-l-2xl"
	/>

	<div class="flex flex-col md:flex-row gap-6">
		<a
			href="/transcription/{tr.id}"
			class="flex-1 flex flex-col md:flex-row gap-6 text-inherit hover:text-inherit"
		>
			<!-- Visual Column -->
			<div
				class="hidden md:flex flex-col items-center justify-center bg-base-300/50 rounded-xl p-4 min-w-[100px] border border-base-content/5 group-hover:border-primary/20 transition-colors"
			>
				<div
					class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-2"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-6 h-6"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
						<path d="M19 10v2a7 7 0 0 1-14 0v-2" />
						<line x1="12" y1="19" x2="12" y2="23" />
						<line x1="8" y1="23" x2="16" y2="23" />
					</svg>
				</div>
				<span class="text-[10px] font-bold uppercase tracking-wider opacity-60">{duration}</span>
			</div>

			<!-- Content Column -->
			<div class="flex-1 flex flex-col justify-between space-y-3">
				<div>
					<div class="flex flex-wrap items-center gap-2 mb-2">
						<h3
							class="text-lg font-bold text-base-content group-hover:text-primary transition-colors truncate max-w-md"
						>
							{fileName}
						</h3>
						<div class="flex flex-wrap gap-2">
							<div
								class="badge badge-outline badge-sm opacity-70 group-hover:opacity-100 transition-opacity uppercase font-mono text-[10px]"
							>
								{tr.modelSize}
							</div>
							<div
								class="badge badge-primary badge-sm font-bold uppercase text-[10px] tracking-tight"
							>
								{tr.task || 'transcribe'}
							</div>
							<div class="badge badge-ghost badge-sm font-mono text-[10px]">
								{tr.result.language}
							</div>
						</div>
					</div>

					<p
						class="text-sm text-base-content/70 italic line-clamp-2 md:line-clamp-3 mb-3 leading-relaxed"
					>
						"{snippet}"
					</p>
				</div>

				<div class="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs font-medium opacity-60">
					<div class="flex items-center gap-1.5 md:hidden">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-3.5 h-3.5"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg
						>
						{duration}
					</div>
					<div class="flex items-center gap-1.5">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-3.5 h-3.5"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line
								x1="16"
								y1="2"
								x2="16"
								y2="6"
							/><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg
						>
						{date}
					</div>
					<div class="flex items-center gap-1.5">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-3.5 h-3.5"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline
								points="14 2 14 8 20 8"
							/><line x1="16" y1="13" x2="8" y2="13" /><line
								x1="16"
								y1="17"
								x2="8"
								y2="17"
							/><polyline points="10 9 9 9 8 9" /></svg
						>
						{wordCount}
						{$t('words')}
					</div>
					{#if tr.result.processing_duration}
						<div class="flex items-center gap-1.5">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="w-3.5 h-3.5"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg
							>
							{$t('took')}
							{tr.result.processing_duration.toFixed(1)}s
						</div>
					{/if}
				</div>
			</div>
		</a>

		<!-- Action Column -->
		<div
			class="flex md:flex-col items-center justify-center gap-2 border-t md:border-t-0 md:border-l border-base-content/10 pt-4 md:pt-0 md:pl-6 min-w-[60px]"
		>
			<a
				href="/editor/{tr.id}"
				class="btn btn-square btn-ghost btn-sm hover:bg-primary hover:text-primary-content transition-all"
				title={$t('edit')}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path
						d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
					/></svg
				>
			</a>

			<button
				on:click={download}
				onclick="modalDownloadOptions.showModal()"
				class="btn btn-square btn-ghost btn-sm hover:bg-secondary hover:text-secondary-content transition-all"
				title={$t('download')}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline
						points="7 10 12 15 17 10"
					/><line x1="12" y1="15" x2="12" y2="3" /></svg
				>
			</button>

			<button
				on:click={translate}
				class="btn btn-square btn-ghost btn-sm hover:bg-accent hover:text-accent-content transition-all"
				title="Translate"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					><path d="m5 8 6 6" /><path d="m4 14 6-6 2-3" /><path d="M2 5h12" /><path
						d="M7 2h1"
					/><path d="m22 22-5-10-5 10" /><path d="M14 18h6" /></svg
				>
			</button>

			<button
				on:click={deleteTranscription(tr.id)}
				class="btn btn-square btn-ghost btn-sm hover:bg-error hover:text-error-content transition-all text-error/60"
				title="Delete"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					><polyline points="3 6 5 6 21 6" /><path
						d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
					/><line x1="10" y1="11" x2="10" y2="17" /><line x1="14" y1="11" x2="14" y2="17" /></svg
				>
			</button>
		</div>
	</div>
</div>
