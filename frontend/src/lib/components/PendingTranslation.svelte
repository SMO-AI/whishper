<script>
	import { fade } from 'svelte/transition';
	export let tr;
	$: fileName = tr.fileName ? tr.fileName.split('_WHSHPR_')[1] : 'Initializing...';
</script>

<div
	class="group relative bg-base-200/30 border border-secondary/30 border-dashed rounded-2xl p-5 md:p-6 transition-all duration-300 shadow-sm mt-4 animate-pulse"
	in:fade
>
	<div class="flex flex-col md:flex-row gap-6 items-center">
		<!-- Visual Column -->
		<div
			class="hidden md:flex flex-col items-center justify-center bg-secondary/10 rounded-xl p-4 min-w-[100px] border border-secondary/10"
		>
			<div
				class="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center text-secondary mb-2"
			>
				<span class="loading loading-dots loading-md" />
			</div>
			<span class="text-[10px] font-bold uppercase tracking-wider opacity-60 italic text-secondary"
				>Translating</span
			>
		</div>

		<!-- Content Column -->
		<div class="flex-1 flex flex-col justify-center space-y-2 text-center md:text-left">
			<div class="flex flex-wrap items-center justify-center md:justify-start gap-2 mb-1">
				<h3 class="text-lg font-bold text-base-content/60 truncate max-w-md">
					{fileName}
				</h3>
				<div class="badge badge-secondary badge-outline badge-sm font-bold uppercase text-[10px]">
					Processing
				</div>
			</div>
			<p class="text-sm font-mono opacity-50">
				Converting your text to the target language. Please wait...
			</p>
		</div>
	</div>
</div>
