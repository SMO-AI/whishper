<script>
	import { deleteTranscription } from '$lib/utils.js';
	import { fade } from 'svelte/transition';
	export let tr;
</script>

<div
	class="group relative bg-error/5 border border-error/20 rounded-2xl p-5 md:p-6 transition-all duration-300 shadow-sm hover:shadow-md mt-4"
	in:fade
>
	<!-- Left marker -->
	<div class="absolute inset-y-0 left-0 w-1 bg-error rounded-l-2xl" />

	<div class="flex flex-col md:flex-row gap-6 items-center">
		<!-- Visual Column -->
		<div
			class="hidden md:flex flex-col items-center justify-center bg-error/10 rounded-xl p-4 min-w-[100px] border border-error/10"
		>
			<div
				class="w-12 h-12 rounded-full bg-error/20 flex items-center justify-center text-error mb-2"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-6 h-6"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="3"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<line x1="18" y1="6" x2="6" y2="18" />
					<line x1="6" y1="6" x2="18" y2="18" />
				</svg>
			</div>
			<span class="text-[10px] font-bold uppercase tracking-wider text-error">Failed</span>
		</div>

		<!-- Content Column -->
		<div class="flex-1 flex flex-col justify-center space-y-2 text-center md:text-left">
			<div class="flex flex-wrap items-center justify-center md:justify-start gap-2 mb-1">
				<h3 class="text-lg font-bold text-error/80 truncate max-w-md">
					id-{tr.id}
				</h3>
				<div class="badge badge-error badge-sm font-bold uppercase text-[10px]">Error</div>
			</div>
			<p class="text-sm font-mono text-error/60">
				Transcription crashed or failed to initialize. Please check logs or try a different model.
			</p>
		</div>

		<!-- Action Column -->
		<div class="flex items-center justify-center pt-4 md:pt-0 md:pl-6">
			<button
				on:click={deleteTranscription(tr.id)}
				class="btn btn-error btn-outline btn-sm font-bold gap-2"
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
					/></svg
				>
				Remove
			</button>
		</div>
	</div>
</div>
