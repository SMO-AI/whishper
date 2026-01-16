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

	<div class="w-full max-w-md relative z-10">
		<slot />
	</div>

	<Toaster />
</div>
