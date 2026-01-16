<script>
	import { fade } from 'svelte/transition';
	export let tr;
	$: fileName = tr.fileName ? tr.fileName.split('_WHSHPR_')[1] : 'Initializing...';
</script>

<div
	class="group relative bg-base-200/30 border border-base-300 border-dashed rounded-2xl p-5 md:p-6 transition-all duration-300 shadow-sm mt-4 animate-pulse"
	in:fade
>
	<div class="flex flex-col md:flex-row gap-6 items-center">
		<!-- Visual Column -->
		<div
			class="hidden md:flex flex-col items-center justify-center bg-base-300/30 rounded-xl p-4 min-w-[100px] border border-base-content/5"
		>
			<div
				class="w-12 h-12 rounded-full bg-info/10 flex items-center justify-center text-info mb-2"
			>
				<span class="loading loading-ring loading-md"></span>
			</div>
			<span class="text-[10px] font-bold uppercase tracking-wider opacity-60 italic"
				>Processing</span
			>
		</div>

		<!-- Content Column -->
		<div class="flex-1 flex flex-col justify-center space-y-2 text-center md:text-left">
			<div class="flex flex-wrap items-center justify-center md:justify-start gap-2 mb-1">
				<h3 class="text-lg font-bold text-base-content/60 truncate max-w-md">
					{fileName}
				</h3>
				<div class="badge badge-info badge-outline badge-sm font-bold uppercase text-[10px]">
					Pending
				</div>
			</div>
			<p class="text-sm font-mono opacity-50">
				Whisper is analyzing your audio file. This may take a moment depending on the file size and
				model...
			</p>
		</div>
	</div>
</div>
