<script>
	import { Toaster } from 'svelte-french-toast';
	import '../../app.css';
</script>

<div
	class="min-h-screen flex items-center justify-center p-4 bg-base-200/50 relative overflow-hidden"
>
	<!-- Background Blobs -->
	<div class="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
		<div
			class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[100px]"
		/>
		<div
			class="absolute top-[40%] -right-[10%] w-[40%] h-[40%] bg-secondary/20 rounded-full blur-[100px]"
		/>
	</div>

	<!-- Back to Home -->
	<a
		href="/"
		class="absolute top-6 left-6 z-20 btn btn-ghost btn-sm gap-2 opacity-70 hover:opacity-100 transition-all group"
	>
		<svg
			xmlns="http://www.w3.org/2000/svg"
			class="w-4 h-4 group-hover:-translate-x-1 transition-transform"
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
		Home
	</a>

	<div class="w-full max-w-md relative z-10">
		<slot />
	</div>

	<Toaster />
</div>
