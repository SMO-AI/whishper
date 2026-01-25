<script>
	import { theme, t, locale } from '$lib/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';

	onMount(async () => {
		locale.set('en');
		if (supabase) {
			const {
				data: { session }
			} = await supabase.auth.getSession();
			if (session) {
				goto('/app');
			}
		}
	});
</script>

<svelte:head>
	<title>{$t('app_name')} - AI Audio to Text Transcription | Fast & Accurate</title>
	<meta
		name="description"
		content="Professional AI transcription for audio and video. Convert interviews, meetings, and content into perfect text in seconds."
	/>
	<meta
		name="keywords"
		content="transcription, AI, audio to text, video to text, Whisper V3, speech recognition, Scriptus"
	/>
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://scriptus.online/" />
	<meta property="og:title" content="{$t('app_name')} - AI Audio to Text Transcription" />
	<meta property="og:description" content={$t('hero_desc')} />
	<meta property="og:image" content="https://scriptus.online/og-image.png" />
	<meta property="twitter:card" content="summary_large_image" />
	<meta property="twitter:title" content="{$t('app_name')} - AI Audio to Text Transcription" />
	<meta property="twitter:description" content={$t('hero_desc')} />
	<meta property="twitter:image" content="https://scriptus.online/og-image.png" />
	<link rel="canonical" href="https://scriptus.online/" />
</svelte:head>

<div
	class="min-h-screen bg-[#050510] text-[#E0E0E0] overflow-x-hidden relative font-sans selection:bg-primary selection:text-white"
>
	<!-- Background Gradients -->
	<div class="fixed inset-0 z-0 pointer-events-none overflow-hidden">
		<div
			class="absolute top-[-10%] left-[-10%] w-[150vw] sm:w-[800px] h-[800px] bg-indigo-600/20 rounded-full blur-[120px] mix-blend-screen opacity-40 animate-pulse"
			style="animation-duration: 8s;"
		/>
		<div
			class="absolute bottom-[-10%] right-[-10%] w-[150vw] sm:w-[600px] h-[600px] bg-fuchsia-600/20 rounded-full blur-[100px] mix-blend-screen opacity-40 animate-pulse"
			style="animation-duration: 10s; animation-delay: 2s;"
		/>
	</div>

	<nav
		class="fixed top-0 left-0 w-full z-50 transition-all duration-300 border-b border-white/5 bg-[#050510]/70 backdrop-blur-lg"
	>
		<div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 sm:h-20 flex items-center justify-between">
			<a href="/" class="flex items-center gap-2 group cursor-pointer">
				<img
					src="/logo.svg"
					alt="{$t('app_name')} Logo"
					class="w-8 h-8 sm:w-10 sm:h-10 transition-transform group-hover:scale-110"
				/>
				<span
					class="text-lg sm:text-xl font-bold tracking-tight text-white group-hover:opacity-80 transition-opacity"
					>{$t('app_name')}</span
				>
			</a>

			<div class="hidden md:flex items-center gap-8 text-sm font-medium text-white/60">
				<a href="#features" class="hover:text-white transition-colors">{$t('features_nav')}</a>
				<a href="#pricing" class="hover:text-white transition-colors">{$t('pricing_nav')}</a>
				<a href="#testimonials" class="hover:text-white transition-colors">{$t('reviews_nav')}</a>
			</div>

			<div class="flex items-center gap-4">
				<a
					href="/auth/login"
					class="text-sm font-medium text-white/70 hover:text-white transition-colors hidden sm:block"
					>{$t('sign_in')}</a
				>
				<a
					href="/auth/register"
					class="relative inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-2.5 overflow-hidden font-medium text-white transition duration-300 ease-out border border-white/10 rounded-full group hover:border-primary/50 bg-white/5 hover:bg-white/10 text-sm sm:text-base"
				>
					<span
						class="absolute inset-0 flex items-center justify-center w-full h-full text-white duration-300 -translate-x-full bg-primary group-hover:translate-x-0 ease"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"
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
						>{$t('get_started')}</span
					>
					<span class="relative invisible">{$t('get_started')}</span>
				</a>
			</div>
		</div>
	</nav>

	<main class="relative z-10 pt-24 sm:pt-32 pb-20 px-4 sm:px-6">
		<section class="max-w-7xl mx-auto flex flex-col items-center text-center mb-20 sm:mb-32">
			<div
				class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] sm:text-xs font-medium text-primary mb-6 sm:mb-8 animate-fade-in-up"
			>
				<span class="relative flex h-2 w-2">
					<span
						class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"
					/>
					<span class="relative inline-flex rounded-full h-2 w-2 bg-primary" />
				</span>
				{$t('hero_badge')}
			</div>

			<h1
				class="text-4xl sm:text-6xl md:text-8xl font-bold tracking-tight mb-6 sm:mb-8 leading-[1.1] animate-fade-in-up delay-100 px-2"
			>
				{$t('hero_title_1')} <br />
				<span
					class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-primary to-fuchsia-400"
					>{$t('hero_title_2')}</span
				>
			</h1>

			<p
				class="text-base sm:text-lg md:text-xl text-white/50 max-w-2xl mx-auto mb-8 sm:mb-10 leading-relaxed animate-fade-in-up delay-200 px-4"
			>
				{$t('hero_desc')} <span class="text-white/80">{$t('hero_guarantee')}</span>
			</p>

			<div
				class="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up delay-300 w-full sm:w-auto px-4"
			>
				<a
					href="/auth/register"
					class="btn btn-primary btn-md sm:btn-lg rounded-full w-full sm:px-10 shadow-[0_0_30px_-5px_theme(colors.primary)] hover:shadow-[0_0_50px_-5px_theme(colors.primary)] border-none text-white transition-all hover:scale-105"
				>
					{$t('start_free')}
				</a>
				<a
					href="/auth/login"
					class="btn btn-ghost btn-md sm:btn-lg rounded-full w-full sm:px-8 text-white/60 hover:text-white hover:bg-white/5 border border-white/5 hover:border-white/20"
				>
					{$t('login')}
				</a>
			</div>

			<div class="mt-12 sm:mt-16 w-full max-w-2xl mx-auto animate-fade-in-up delay-500 px-2">
				<a
					href="/auth/register"
					class="group relative flex flex-col items-center justify-center w-full h-48 sm:h-64 rounded-3xl border-2 border-dashed border-white/20 hover:border-primary/50 bg-white/5 hover:bg-white/10 transition-all duration-300 backdrop-blur-sm cursor-pointer overflow-hidden"
				>
					<div
						class="absolute inset-0 bg-primary/20 blur-[100px] opacity-0 group-hover:opacity-100 transition-opacity duration-500"
					/>
					<div
						class="relative z-10 flex flex-col items-center text-center p-4 sm:p-6 space-y-3 sm:space-y-4"
					>
						<div
							class="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-tr from-white/10 to-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:border-primary/50 transition-all duration-300"
						>
							<svg
								class="w-6 h-6 sm:w-8 sm:h-8 text-white/70 group-hover:text-primary transition-colors"
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
								class="text-lg sm:text-xl font-medium text-white group-hover:text-primary-content transition-colors"
							>
								{$t('drop_file')}
							</p>
							<p class="text-xs sm:text-sm text-white/40">{$t('supported_formats')}</p>
						</div>
						<div
							class="inline-flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/5 text-[10px] sm:text-xs text-white/30 mt-2"
						>
							<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
							{$t('ready_to_process')}
						</div>
					</div>
				</a>
			</div>
		</section>

		<section id="features" class="max-w-7xl mx-auto mb-20 sm:mb-32">
			<div class="text-center mb-12 sm:mb-16 px-4">
				<h2 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
					{$t('features_title')} <br /><span class="text-white/40">{$t('features_subtitle')}</span>
				</h2>
			</div>

			<div
				class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-6 gap-4 sm:gap-6 auto-rows-[minmax(180px,auto)]"
			>
				<div
					class="sm:col-span-2 md:col-span-4 rounded-3xl p-6 sm:p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors group relative overflow-hidden"
				>
					<div
						class="absolute top-0 right-0 p-6 sm:p-8 opacity-10 group-hover:opacity-20 transition-opacity hidden sm:block"
					>
						<svg class="w-24 h-24 sm:w-32 sm:h-32" fill="currentColor" viewBox="0 0 24 24"
							><path d="M13 10V3L4 14h7v7l9-11h-9z" /></svg
						>
					</div>
					<h3 class="text-xl sm:text-2xl font-bold mb-2">{$t('lightning_fast')}</h3>
					<p class="text-white/60 text-base sm:text-lg max-w-md">{$t('lightning_fast_desc')}</p>
					<div
						class="mt-6 sm:mt-8 flex items-end gap-2 text-3xl sm:text-4xl font-mono text-primary"
					>
						{$t('lightning_fast_stat').split(' ')[0]}
						<span class="text-xs sm:text-sm text-white/40 mb-1 sm:mb-2 font-sans"
							>{$t('lightning_fast_stat').split(' ').slice(1).join(' ')}</span
						>
					</div>
				</div>

				<div
					class="sm:col-span-2 md:col-span-2 rounded-3xl p-6 sm:p-8 bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-primary/30 transition-colors flex flex-col justify-between"
				>
					<div>
						<h3 class="text-xl sm:text-2xl font-bold mb-2">{$t('precision')}</h3>
						<p class="text-white/60">{$t('precision_desc')}</p>
					</div>
					<div
						class="text-5xl sm:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 self-end mt-4"
					>
						{$t('precision_stat')}
					</div>
				</div>

				<div
					class="sm:col-span-1 md:col-span-2 rounded-3xl p-6 sm:p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors"
				>
					<div
						class="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/10 flex items-center justify-center mb-4 text-primary"
					>
						<svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							/></svg
						>
					</div>
					<h3 class="text-lg sm:text-xl font-bold mb-2">{$t('private_design')}</h3>
					<p class="text-white/60 text-xs sm:text-sm">{$t('private_design_desc')}</p>
				</div>

				<div
					class="sm:col-span-1 md:col-span-2 rounded-3xl p-6 sm:p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors flex flex-col items-center justify-center text-center"
				>
					<div class="flex -space-x-3 mb-4">
						<div
							class="w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 border-[#050510] bg-white/10 flex items-center justify-center text-[10px] sm:text-xs"
						>
							EN
						</div>
						<div
							class="w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 border-[#050510] bg-white/10 flex items-center justify-center text-[10px] sm:text-xs"
						>
							ES
						</div>
						<div
							class="w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 border-[#050510] bg-white/10 flex items-center justify-center text-[10px] sm:text-xs"
						>
							RU
						</div>
						<div
							class="w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 border-[#050510] bg-white/20 flex items-center justify-center text-[10px] sm:text-xs"
						>
							{$t('multilingual_stat')}
						</div>
					</div>
					<h3 class="text-lg sm:text-xl font-bold">{$t('multilingual')}</h3>
					<p class="text-white/60 text-xs sm:text-sm mt-2">{$t('multilingual_desc')}</p>
				</div>

				<div
					class="sm:col-span-2 md:col-span-2 rounded-3xl p-6 sm:p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors group"
				>
					<h3 class="text-lg sm:text-xl font-bold mb-2">{$t('smart_editor')}</h3>
					<p class="text-white/60 text-xs sm:text-sm mb-4">{$t('smart_editor_desc')}</p>
					<div class="w-full h-1.5 sm:h-2 rounded bg-white/10 overflow-hidden">
						<div
							class="w-2/3 h-full bg-primary/50 group-hover:w-full transition-all duration-1000"
						/>
					</div>
				</div>
			</div>
		</section>

		<section id="pricing" class="max-w-7xl mx-auto mb-20 sm:mb-32 relative">
			<div
				class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full max-w-lg bg-primary/10 blur-[100px] rounded-full pointer-events-none hidden sm:block"
			/>
			<div class="text-center mb-12 sm:mb-16 relative z-10 px-4">
				<h2 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">{$t('pricing_title')}</h2>
				<p class="text-lg sm:text-xl text-white/50">{$t('pricing_subtitle')}</p>
			</div>

			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 relative z-10">
				<!-- Free Plan -->
				<div
					class="rounded-3xl p-6 sm:p-8 bg-white/5 border border-white/10 hover:border-white/20 transition-all flex flex-col"
				>
					<div class="mb-4 text-left">
						<span
							class="px-3 py-1 rounded-full bg-white/10 text-[10px] font-medium text-white/80 uppercase"
							>{$t('starter')}</span
						>
					</div>
					<div class="text-left">
						<h3 class="text-3xl sm:text-4xl font-bold mb-2">$0</h3>
						<p class="text-white/50 text-sm mb-6 sm:mb-8">{$t('perfect_testing')}</p>
					</div>
					<ul class="space-y-3 sm:space-y-4 mb-6 sm:mb-8 flex-1 text-left">
						<li class="flex items-start gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0"
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
							{$t('min_per_month')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0"
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
							{$t('std_accuracy')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0"
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
							{$t('single_speaker')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0"
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
							{$t('mp3_wav_export')}
						</li>
					</ul>
					<a
						href="/auth/register"
						class="btn btn-outline btn-md border-white/20 text-white hover:bg-white hover:text-black w-full rounded-2xl"
						>{$t('get_started')}</a
					>
				</div>

				<!-- Pro Plan -->
				<div
					class="rounded-3xl p-6 sm:p-8 bg-gradient-to-b from-primary/10 to-primary/5 border border-primary/50 relative flex flex-col shadow-2xl shadow-primary/10 sm:scale-105 z-20"
				>
					<div class="absolute top-0 right-0 p-4">
						<div
							class="bg-primary text-white text-[10px] font-bold px-3 py-1 rounded-full shadow-lg uppercase"
						>
							DATA SAFE
						</div>
					</div>
					<div class="mb-4 text-left">
						<span
							class="px-3 py-1 rounded-full bg-primary/20 text-[10px] font-medium text-primary uppercase"
							>{$t('creator')}</span
						>
					</div>
					<div class="text-left">
						<h3 class="text-3xl sm:text-4xl font-bold mb-2">
							$7<span class="text-lg text-white/40 font-normal">{$t('per_month')}</span>
						</h3>
						<p class="text-white/50 text-sm mb-6 sm:mb-8">{$t('constant_creation')}</p>
					</div>
					<ul class="space-y-3 sm:space-y-4 mb-6 sm:mb-8 flex-1 text-left">
						<li class="flex items-start gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary mt-0.5 shrink-0"
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
							{$t('buy_more_tokens')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary mt-0.5 shrink-0"
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
							<span
								><strong>{$t('hours_per_month')}</strong>
								{$t('per_month').replace('/', 'per ')}</span
							>
						</li>
						<li class="flex items-start gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary mt-0.5 shrink-0"
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
							{$t('whisper_v3_turbo')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary mt-0.5 shrink-0"
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
							{$t('adv_diarization')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary mt-0.5 shrink-0"
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
							{$t('unlimited_storage')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white">
							<svg
								class="w-5 h-5 text-primary mt-0.5 shrink-0"
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
							{$t('all_export_formats')}
						</li>
					</ul>
					<a
						href="/auth/register"
						class="btn btn-primary btn-md w-full rounded-2xl shadow-lg shadow-primary/25"
						>{$t('start_free_trial')}</a
					>
				</div>

				<!-- Business Plan -->
				<div
					class="rounded-3xl p-6 sm:p-8 bg-white/5 border border-white/10 hover:border-white/20 transition-all flex flex-col sm:col-span-2 lg:col-span-1"
				>
					<div class="mb-4 text-left">
						<span
							class="px-3 py-1 rounded-full bg-white/10 text-[10px] font-medium text-white/80 uppercase"
							>{$t('business')}</span
						>
					</div>
					<div class="text-left">
						<h3 class="text-3xl sm:text-4xl font-bold mb-2">
							$15<span class="text-lg text-white/40 font-normal">{$t('per_month')}</span>
						</h3>
						<p class="text-white/50 text-sm mb-6 sm:mb-8">{$t('team_power')}</p>
					</div>
					<ul class="space-y-3 sm:space-y-4 mb-6 sm:mb-8 flex-1 text-left">
						<li class="flex items-start gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0"
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
							<span
								><strong>{$t('hours_per_month_biz')}</strong>
								{$t('per_month').replace('/', 'per ')}</span
							>
						</li>
						<li class="flex items-start gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0"
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
							{$t('priority_queue')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0"
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
							{$t('priority_queue')}
						</li>
						<li class="flex items-start gap-3 text-sm text-white/80">
							<svg
								class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0"
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
							{$t('team_management')}
						</li>
					</ul>
					<a
						href="/auth/register"
						class="btn btn-outline btn-md border-white/20 text-white hover:bg-white hover:text-black w-full rounded-2xl"
						>{$t('contact_sales')}</a
					>
				</div>
			</div>
		</section>

		<footer
			class="max-w-7xl mx-auto pt-16 sm:pt-20 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-6 text-center sm:text-left"
		>
			<div class="text-white/40 text-xs sm:text-sm">
				© 2026 {$t('app_name')}. {$t('footer_rights')}
			</div>
			<div class="flex gap-6 text-xs sm:text-sm text-white/40">
				<a href="/changelog" class="hover:text-white transition-colors">Changelog</a>
				<a href="#" class="hover:text-white transition-colors">{$t('privacy')}</a>
				<a href="#" class="hover:text-white transition-colors">{$t('terms')}</a>
				<a href="#" class="hover:text-white transition-colors">{$t('contact')}</a>
			</div>
		</footer>
	</main>
</div>

<style>
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
		opacity: 0;
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
