<script>
	import { theme, t } from '$lib/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';

	onMount(async () => {
		const {
			data: { session }
		} = await supabase.auth.getSession();
		if (session) {
			goto('/app');
		}
	});

	// Animation constants or states could go here
</script>

<svelte:head>
	<title>Scriptus - AI Audio to Text Transcription | Fast & Accurate</title>
	<meta
		name="description"
		content="Professional AI transcription for audio and video. Convert interviews, meetings, and content into perfect text in seconds with Whisper V3 Turbo accuracy."
	/>
	<meta
		name="keywords"
		content="transcription, AI, audio to text, video to text, Whisper V3, speech recognition, Scriptus"
	/>

	<!-- Open Graph / Facebook -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://scriptus.online/" />
	<meta property="og:title" content="Scriptus - AI Audio to Text Transcription" />
	<meta
		property="og:description"
		content="Fast, accurate, and secure AI transcription. Convert your media to text in minutes."
	/>
	<meta property="og:image" content="https://scriptus.online/og-image.png" />

	<!-- Twitter -->
	<meta property="twitter:card" content="summary_large_image" />
	<meta property="twitter:url" content="https://scriptus.online/" />
	<meta property="twitter:title" content="Scriptus - AI Audio to Text Transcription" />
	<meta
		property="twitter:description"
		content="Fast, accurate, and secure AI transcription. Convert your media to text in minutes."
	/>
	<meta property="twitter:image" content="https://scriptus.online/og-image.png" />

	<link rel="canonical" href="https://scriptus.online/" />

	<script type="application/ld+json">
		{
			"@context": "https://schema.org",
			"@type": "SoftwareApplication",
			"name": "Scriptus",
			"operatingSystem": "Web",
			"applicationCategory": "MultimediaApplication",
			"offers": {
				"@type": "Offer",
				"price": "0.00",
				"priceCurrency": "USD"
			},
			"description": "Professional AI transcription for audio and video. Convert interviews, meetings, and content into perfect text in seconds."
		}
	</script>
</svelte:head>

<div
	class="min-h-screen bg-[#050510] text-[#E0E0E0] overflow-x-hidden relative font-sans selection:bg-primary selection:text-white"
>
	<!-- Ambient Background Gradients -->
	<div class="fixed inset-0 z-0 pointer-events-none">
		<div
			class="absolute top-[-20%] left-[-10%] w-[800px] h-[800px] bg-indigo-600/20 rounded-full blur-[120px] mix-blend-screen opacity-40 animate-pulse"
			style="animation-duration: 8s;"
		/>
		<div
			class="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-fuchsia-600/20 rounded-full blur-[100px] mix-blend-screen opacity-40 animate-pulse"
			style="animation-duration: 10s; animation-delay: 2s;"
		/>
		<div
			class="absolute top-[40%] left-[30%] w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[80px] mix-blend-screen opacity-30"
		/>
	</div>

	<!-- Navigation -->
	<nav
		class="fixed top-0 left-0 w-full z-50 transition-all duration-300 border-b border-white/5 bg-[#050510]/70 backdrop-blur-lg"
	>
		<div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
			<!-- Logo -->
			<a href="/" class="flex items-center gap-2 group cursor-pointer">
				<img
					src="/logo.svg"
					alt="Scriptus Logo"
					class="w-10 h-10 transition-transform group-hover:scale-110"
				/>
				<span
					class="text-xl font-bold tracking-tight text-white group-hover:opacity-80 transition-opacity"
					>{$t('app_name')}</span
				>
			</a>

			<!-- Desktop Nav Elements (Optional) -->
			<div class="hidden md:flex items-center gap-8 text-sm font-medium text-white/60">
				<a href="#features" class="hover:text-white transition-colors">Features</a>
				<a href="#pricing" class="hover:text-white transition-colors">Pricing</a>
				<a href="#testimonials" class="hover:text-white transition-colors">Reviews</a>
			</div>

			<!-- CTA -->
			<div class="flex items-center gap-4">
				<a
					href="/auth/login"
					class="text-sm font-medium text-white/70 hover:text-white transition-colors hidden md:block"
					>Sign In</a
				>
				<a
					href="/auth/register"
					class="relative inline-flex items-center justify-center px-6 py-2.5 overflow-hidden font-medium text-white transition duration-300 ease-out border border-white/10 rounded-full group hover:border-primary/50 bg-white/5 hover:bg-white/10"
				>
					<span
						class="absolute inset-0 flex items-center justify-center w-full h-full text-white duration-300 -translate-x-full bg-primary group-hover:translate-x-0 ease"
					>
						<svg
							class="w-4 h-4"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M14 5l7 7m0 0l-7 7m7-7H3"
							/></svg
						>
					</span>
					<span
						class="absolute flex items-center justify-center w-full h-full text-white transition-all duration-300 transform group-hover:translate-x-full ease"
						>Get Started</span
					>
					<span class="relative invisible">Get Started</span>
				</a>
			</div>
		</div>
	</nav>

	<!-- Main Content -->
	<main class="relative z-10 pt-32 pb-20 px-6">
		<!-- Hero Section -->
		<section class="max-w-7xl mx-auto flex flex-col items-center text-center mb-32">
			<!-- Badge -->
			<div
				class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-primary mb-8 animate-fade-in-up"
			>
				<span class="relative flex h-2 w-2">
					<span
						class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"
					/>
					<span class="relative inline-flex rounded-full h-2 w-2 bg-primary" />
				</span>
				The Next Gen Transcription is Live
			</div>

			<h1
				class="text-5xl md:text-8xl font-bold tracking-tight mb-8 leading-[1.1] animate-fade-in-up delay-100"
			>
				Audio into Text. <br />
				<span
					class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-primary to-fuchsia-400"
				>
					Fast. Accurate. Done.
				</span>
			</h1>

			<p
				class="text-lg md:text-xl text-white/50 max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up delay-200"
			>
				Stop typing manually. Convert your interviews, meetings, and content into perfect text in
				seconds.
				<span class="text-white/80">Whisper V3 Turbo</span> guarantees human-level accuracy for every
				word.
			</p>

			<div class="flex flex-col sm:flex-row items-center gap-4 animate-fade-in-up delay-300">
				<a
					href="/auth/register"
					class="btn btn-primary btn-lg rounded-full px-10 shadow-[0_0_30px_-5px_theme(colors.primary)] hover:shadow-[0_0_50px_-5px_theme(colors.primary)] border-none text-white transition-all hover:scale-105"
				>
					Start Transcribing Free
				</a>
				<a
					href="/auth/login"
					class="btn btn-ghost btn-lg rounded-full px-8 text-white/60 hover:text-white hover:bg-white/5 border border-white/5 hover:border-white/20"
				>
					{$t('login')}
				</a>
			</div>

			<!-- Upload Visualization (High Conversion Focus) -->
			<div class="mt-16 w-full max-w-2xl mx-auto animate-fade-in-up delay-500">
				<a
					href="/auth/register"
					class="group relative flex flex-col items-center justify-center w-full h-64 rounded-3xl border-2 border-dashed border-white/20 hover:border-primary/50 bg-white/5 hover:bg-white/10 transition-all duration-300 backdrop-blur-sm cursor-pointer overflow-hidden"
				>
					<!-- Glowing Effect on Hover -->
					<div
						class="absolute inset-0 bg-primary/20 blur-[100px] opacity-0 group-hover:opacity-100 transition-opacity duration-500"
					/>

					<div class="relative z-10 flex flex-col items-center text-center p-6 space-y-4">
						<div
							class="w-20 h-20 rounded-full bg-gradient-to-tr from-white/10 to-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:border-primary/50 transition-all duration-300"
						>
							<svg
								class="w-8 h-8 text-white/70 group-hover:text-primary transition-colors"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
								/>
							</svg>
						</div>

						<div class="space-y-1">
							<p
								class="text-xl font-medium text-white group-hover:text-primary-content transition-colors"
							>
								Drop your file here or click to upload
							</p>
							<p class="text-sm text-white/40">Supported formats: MP3, WAV, M4A, MP4</p>
						</div>

						<!-- Fake Progress/Status Pill -->
						<div
							class="inline-flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/5 text-xs text-white/30 mt-4"
						>
							<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
							Ready to process
						</div>
					</div>
				</a>
			</div>
		</section>

		<!-- Features Bento Grid -->
		<section id="features" class="max-w-7xl mx-auto mb-32">
			<div class="text-center mb-16">
				<h2 class="text-3xl md:text-5xl font-bold mb-4">
					Built for Speed & Precision. <br /><span class="text-white/40"
						>No more manual transcription.</span
					>
				</h2>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-6 gap-6 auto-rows-[minmax(180px,auto)]">
				<!-- Speed Card -->
				<div
					class="md:col-span-4 rounded-3xl p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors group relative overflow-hidden"
				>
					<div
						class="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity"
					>
						<svg class="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"
							><path d="M13 10V3L4 14h7v7l9-11h-9z" /></svg
						>
					</div>
					<h3 class="text-2xl font-bold mb-2">Lightning Fast</h3>
					<p class="text-white/60 text-lg max-w-md">
						Process hours of audio in minutes. Our optimized engine runs up to 10x faster than
						real-time.
					</p>
					<div class="mt-8 flex items-end gap-2 text-4xl font-mono text-primary">
						10x <span class="text-sm text-white/40 mb-2 font-sans">Faster</span>
					</div>
				</div>

				<!-- Accuracy Card -->
				<div
					class="md:col-span-2 rounded-3xl p-8 bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-primary/30 transition-colors flex flex-col justify-between"
				>
					<div>
						<h3 class="text-2xl font-bold mb-2">Precision</h3>
						<p class="text-white/60">Powered by Whisper V3.</p>
					</div>
					<div
						class="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 self-end"
					>
						99.9%
					</div>
				</div>

				<!-- Privacy Card -->
				<div
					class="md:col-span-2 rounded-3xl p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors"
				>
					<div
						class="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-4 text-primary"
					>
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							/></svg
						>
					</div>
					<h3 class="text-xl font-bold mb-2">Private by Design</h3>
					<p class="text-white/60 text-sm">
						Your data is encrypted at rest and in transit. We don't train our models on your files.
					</p>
				</div>

				<!-- Languages Card -->
				<div
					class="md:col-span-2 rounded-3xl p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors flex flex-col items-center justify-center text-center"
				>
					<div class="flex -space-x-3 mb-4">
						<div
							class="w-10 h-10 rounded-full border-2 border-[#050510] bg-white/10 flex items-center justify-center text-xs"
						>
							EN
						</div>
						<div
							class="w-10 h-10 rounded-full border-2 border-[#050510] bg-white/10 flex items-center justify-center text-xs"
						>
							ES
						</div>
						<div
							class="w-10 h-10 rounded-full border-2 border-[#050510] bg-white/10 flex items-center justify-center text-xs"
						>
							FR
						</div>
						<div
							class="w-10 h-10 rounded-full border-2 border-[#050510] bg-white/20 flex items-center justify-center text-xs"
						>
							+90
						</div>
					</div>
					<h3 class="text-xl font-bold">Multilingual</h3>
					<p class="text-white/60 text-sm mt-2">Auto-detection support for over 90 languages.</p>
				</div>

				<!-- Editor Card -->
				<div
					class="md:col-span-2 rounded-3xl p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors group"
				>
					<h3 class="text-xl font-bold mb-2">Smart Editor</h3>
					<p class="text-white/60 text-sm mb-4">
						Edit transcripts with ease. Timestamps, speakers, and export options included.
					</p>
					<div class="w-full h-2 rounded bg-white/10 overflow-hidden">
						<div
							class="w-2/3 h-full bg-primary/50 group-hover:w-full transition-all duration-1000"
						/>
					</div>
				</div>
			</div>
		</section>

		<!-- Pricing Section -->
		<section id="pricing" class="max-w-7xl mx-auto mb-32 relative">
			<!-- Background Glow -->
			<div
				class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full max-w-lg bg-primary/20 blur-[120px] rounded-full pointer-events-none"
			/>

			<div class="text-center mb-16 relative z-10">
				<h2 class="text-3xl md:text-5xl font-bold mb-4">Simple, Transparent Pricing.</h2>
				<p class="text-xl text-white/50">Start for free, upgrade when you need more power.</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
				<!-- Free Plan -->
				<div
					class="rounded-3xl p-8 bg-white/5 border border-white/10 hover:border-white/20 transition-all flex flex-col"
				>
					<div class="mb-4">
						<span class="px-3 py-1 rounded-full bg-white/10 text-xs font-medium text-white/80"
							>Starter</span
						>
					</div>
					<h3 class="text-4xl font-bold mb-2">$0</h3>
					<p class="text-white/50 mb-8">Perfect for testing the waters.</p>

					<ul class="space-y-4 mb-8 flex-1">
						<li class="flex items-center gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							15 minutes per month
						</li>
						<li class="flex items-center gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							Standard Accuracy (Whisper V2)
						</li>
						<li class="flex items-center gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							Single Speaker Detection
						</li>
						<li class="flex items-center gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							MP3, WAV export
						</li>
					</ul>

					<a
						href="/auth/register"
						class="btn btn-outline border-white/20 text-white hover:bg-white hover:text-black w-full rounded-2xl"
						>Get Started</a
					>
				</div>

				<!-- Pro Plan (Main) -->
				<div
					class="rounded-3xl p-8 bg-gradient-to-b from-primary/10 to-primary/5 border border-primary/50 relative flex flex-col transform md:-translate-y-4 shadow-2xl shadow-primary/10"
				>
					<div class="absolute top-0 right-0 p-4">
						<div class="bg-primary text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
							DATA SAFE
						</div>
					</div>
					<div class="mb-4">
						<span class="px-3 py-1 rounded-full bg-primary/20 text-xs font-medium text-primary"
							>Creator</span
						>
					</div>
					<h3 class="text-4xl font-bold mb-2">
						$15<span class="text-lg text-white/40 font-normal">/mo</span>
					</h3>
					<p class="text-white/50 mb-8">For constant content creation.</p>

					<ul class="space-y-4 mb-8 flex-1">
						<li class="flex items-center gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							<strong>10 Hours</strong> per month
						</li>
						<li class="flex items-center gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							<strong>Whisper V3 Turbo</strong> (Best)
						</li>
						<li class="flex items-center gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							Advanced Speaker Diarization
						</li>
						<li class="flex items-center gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							Unlimited Cloud Storage
						</li>
						<li class="flex items-center gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							SRT, VTT, PDF, TXT Export
						</li>
					</ul>

					<a
						href="/auth/register"
						class="btn btn-primary w-full rounded-2xl shadow-lg shadow-primary/25"
						>Start Free Trial</a
					>
				</div>

				<!-- Business Plan -->
				<div
					class="rounded-3xl p-8 bg-white/5 border border-white/10 hover:border-white/20 transition-all flex flex-col"
				>
					<div class="mb-4">
						<span class="px-3 py-1 rounded-full bg-white/10 text-xs font-medium text-white/80"
							>Business</span
						>
					</div>
					<h3 class="text-4xl font-bold mb-2">
						$49<span class="text-lg text-white/40 font-normal">/mo</span>
					</h3>
					<p class="text-white/50 mb-8">Maximum power for teams.</p>

					<ul class="space-y-4 mb-8 flex-1">
						<li class="flex items-center gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							<strong>50 Hours</strong> per month
						</li>
						<li class="flex items-center gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							Priority Processing Queue
						</li>
						<li class="flex items-center gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							API Access
						</li>
						<li class="flex items-center gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/></svg
							>
							Team Management
						</li>
					</ul>

					<a
						href="/auth/register"
						class="btn btn-outline border-white/20 text-white hover:bg-white hover:text-black w-full rounded-2xl"
						>Contact Sales</a
					>
				</div>
			</div>
		</section>

		<!-- Footer -->
		<footer
			class="max-w-7xl mx-auto pt-20 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6"
		>
			<div class="text-white/40 text-sm">© 2026 {$t('app_name')}. All rights reserved.</div>
			<div class="flex gap-6 text-sm text-white/40">
				<a href="#" class="hover:text-white transition-colors">Privacy</a>
				<a href="#" class="hover:text-white transition-colors">Terms</a>
				<a href="#" class="hover:text-white transition-colors">Contact</a>
			</div>
		</footer>
	</main>
</div>

<style>
	/* Custom Utilities/Animations if needed */
	.perspective-1000 {
		perspective: 1000px;
	}

	@keyframes fade-in-up {
		0% {
			opacity: 0;
			transform: translateY(20px);
		}
		100% {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.animate-fade-in-up {
		animation: fade-in-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
		opacity: 0; /* Star hidden */
	}

	.delay-100 {
		animation-delay: 0.1s;
	}
	.delay-200 {
		animation-delay: 0.2s;
	}
	.delay-300 {
		animation-delay: 0.3s;
	}
	.delay-500 {
		animation-delay: 0.5s;
	}
</style>
