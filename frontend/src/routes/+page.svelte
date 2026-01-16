<script>
	import { theme } from '$lib/stores';
</script>

<div class="min-h-screen bg-base-100 relative overflow-hidden">
	<!-- Background Gradients -->
	<div class="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
		<div
			class="absolute -top-24 -left-24 w-96 h-96 bg-primary/20 rounded-full blur-3xl opacity-50 mix-blend-screen animate-pulse"
		/>
		<div
			class="absolute top-1/2 right-0 w-[500px] h-[500px] bg-secondary/20 rounded-full blur-3xl opacity-30 mix-blend-screen animate-pulse"
			style="animation-delay: 2s"
		/>
	</div>

	<!-- Navigation -->
	<nav class="relative z-10 px-6 py-6 flex items-center justify-between max-w-7xl mx-auto">
		<div class="flex items-center gap-3">
			<div
				class="w-10 h-10 bg-gradient-to-tr from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-6 h-6 text-white"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
					/>
				</svg>
			</div>
			<span
				class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary"
				>Scriptus</span
			>
		</div>
		<div class="flex items-center gap-4">
			<a href="/auth/login" class="btn btn-ghost hover:bg-base-200 transition-colors">Sign In</a>
			<a
				href="/auth/register"
				class="btn btn-primary rounded-full px-6 shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all hover:-translate-y-0.5"
				>Get Started</a
			>
		</div>
	</nav>

	<!-- Hero Section -->
	<main class="relative z-10 pt-20 pb-32 px-6">
		<div class="max-w-5xl mx-auto text-center">
			<div
				class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-base-200/50 backdrop-blur-sm border border-base-content/10 mb-8 animate-fade-in-up"
			>
				<span class="w-2 h-2 rounded-full bg-success" />
				<span class="text-xs font-medium uppercase tracking-wider opacity-80"
					>v2.0 Now Available</span
				>
			</div>

			<h1 class="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 leading-tight">
				Transcribe Audio <br />
				<span class="bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary"
					>Faster Than Real-Time</span
				>
			</h1>

			<p class="text-lg md:text-xl opacity-70 max-w-2xl mx-auto mb-12 leading-relaxed">
				Transform your audio/video files into text instantly with state-of-the-art AI. Secure,
				private, and insanely accurate transcription for professionals.
			</p>

			<div class="flex flex-col md:flex-row items-center justify-center gap-4 mb-20">
				<a
					href="/auth/register"
					class="btn btn-primary btn-lg rounded-2xl px-8 w-full md:w-auto shadow-xl shadow-primary/20 hover:shadow-2xl hover:shadow-primary/30 transition-all group"
				>
					Start Transcribing Free
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 7l5 5m0 0l-5 5m5-5H6"
						/>
					</svg>
				</a>
				<a
					href="#how-it-works"
					class="btn btn-ghost btn-lg rounded-2xl px-8 w-full md:w-auto border border-base-content/10 hover:bg-base-200/50"
				>
					How it works
				</a>
			</div>

			<!-- Simple UI Mockup/Preview -->
			<div
				class="relative max-w-4xl mx-auto rounded-3xl p-2 bg-gradient-to-b from-base-content/10 to-transparent backdrop-blur-sm"
			>
				<div
					class="rounded-2xl overflow-hidden shadow-2xl bg-base-100 border border-base-content/5 aspect-[16/9] flex items-center justify-center relative"
				>
					<div class="absolute inset-0 bg-base-300 animate-pulse opacity-50" />
					<div class="z-10 text-center">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-16 h-16 mx-auto mb-4 opacity-20"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
							/>
						</svg>
						<p class="opacity-50 font-medium">App Interface Preview</p>
					</div>
				</div>
			</div>
		</div>
	</main>
</div>
