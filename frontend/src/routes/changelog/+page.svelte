<script>
	import { t, locale } from '$lib/stores';
	import { onMount } from 'svelte';

	const updatesData = [
		{
			version: 'v2.0.0',
			date: '2026-01-17',
			category: 'Major Update',
			highlight: true,
			era: 'modern',
			en: {
				title: 'The AI Revolution',
				description:
					'A complete overhaul of the platform with cutting-edge AI integrations and a premium UI redesign.',
				changes: [
					{
						type: 'feat',
						text: 'Complete UI/UX Redesign with modern glassmorphism and animations.'
					},
					{
						type: 'feat',
						text: 'Full Supabase integration for secure Auth and real-time database.'
					},
					{ type: 'feat', text: 'Ultra-fast transcription support via Groq API integration.' },
					{ type: 'feat', text: 'Comprehensive SEO & PWA optimizations for better accessibility.' },
					{ type: 'feat', text: 'New interactive media player for audio and video transcriptions.' }
				]
			},
			ru: {
				title: 'Революция ИИ',
				description:
					'Полное обновление платформы с передовыми интеграциями ИИ и премиальным редизайном интерфейса.',
				changes: [
					{
						type: 'feat',
						text: 'Полный редизайн UI/UX с современным стеклянным эффектом и анимациями.'
					},
					{
						type: 'feat',
						text: 'Полная интеграция Supabase для безопасной авторизации и базы данных реального времени.'
					},
					{ type: 'feat', text: 'Поддержка сверхбыстрой транскрибации через интеграцию Groq API.' },
					{ type: 'feat', text: 'Комплексная оптимизация SEO и PWA для лучшей доступности.' },
					{ type: 'feat', text: 'Новый интерактивный медиаплеер для аудио и видео транскрипций.' }
				]
			}
		},
		{
			version: 'v1.8.0',
			date: '2026-01-16',
			category: 'Feature Update',
			era: 'modern',
			en: {
				title: 'Global Expansion',
				description: 'Breaking language barriers and improving the editing experience.',
				changes: [
					{
						type: 'feat',
						text: 'Internationalization (i18n) support with Russian and English translations.'
					},
					{ type: 'feat', text: 'Unified Transcription & Translation task selection.' },
					{ type: 'feat', text: 'Dedicated transcription detail view with synchronized editor.' },
					{
						type: 'refactor',
						text: 'Streamlined Docker build process and improved proxy configurations.'
					}
				]
			},
			ru: {
				title: 'Глобальное расширение',
				description: 'Разрушение языковых барьеров и улучшение процесса редактирования.',
				changes: [
					{
						type: 'feat',
						text: 'Поддержка интернационализации (i18n) с переводами на русский и английский.'
					},
					{ type: 'feat', text: 'Единая система выбора задач транскрибации и перевода.' },
					{
						type: 'feat',
						text: 'Выделенный вид деталей транскрипции с синхронизированным редактором.'
					},
					{
						type: 'refactor',
						text: 'Оптимизированный процесс сборки Docker и улучшенные настройки прокси.'
					}
				]
			}
		},
		{
			version: 'v1.5.0',
			date: '2025-08-15',
			category: 'Legacy Support',
			era: 'legacy',
			en: {
				title: 'Stable Foundation',
				description: 'Inherited stability from the original Whishper project.',
				changes: [
					{ type: 'fix', text: 'Improved Docker image build reliability and volume management.' },
					{ type: 'config', text: 'Dynamic environment variable support via SvelteKit.' },
					{ type: 'fix', text: 'Optimized Nginx buffering for large audio file processing.' }
				]
			},
			ru: {
				title: 'Стабильный фундамент',
				description: 'Унаследованная стабильность оригинального проекта Whishper.',
				changes: [
					{ type: 'fix', text: 'Улучшенная надежность сборки Docker-образов и управление томами.' },
					{ type: 'config', text: 'Поддержка динамических переменных окружения через SvelteKit.' },
					{
						type: 'fix',
						text: 'Оптимизированная буферизация Nginx для обработки больших аудиофайлов.'
					}
				]
			}
		},
		{
			version: 'v1.1.1',
			date: '2023-09-25',
			era: 'legacy',
			en: {
				title: 'Initial Core Fixes',
				changes: [
					{ type: 'fix', text: 'Corrected Japanese language code mapping (jp -> ja).' },
					{ type: 'chore', text: 'Bumped faster-whisper version to 0.9.0.' }
				]
			},
			ru: {
				title: 'Первые исправления ядра',
				changes: [
					{ type: 'fix', text: 'Исправлен код японского языка (jp -> ja).' },
					{ type: 'chore', text: 'Обновлена версия faster-whisper до 0.9.0.' }
				]
			}
		}
	];

	$: modernUpdates = updatesData
		.filter((u) => u.era === 'modern')
		.map((u) => ({
			...u,
			...(u[$locale] || u['en'])
		}));

	$: legacyUpdates = updatesData
		.filter((u) => u.era === 'legacy')
		.map((u) => ({
			...u,
			...(u[$locale] || u['en'])
		}));

	function getTagClass(type) {
		switch (type) {
			case 'feat':
				return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
			case 'fix':
				return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
			case 'refactor':
				return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
			default:
				return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
		}
	}
</script>

<svelte:head>
	<title>{$locale === 'ru' ? 'История изменений' : 'Changelog'} - {$t('app_name')}</title>
</svelte:head>

<div
	class="min-h-screen bg-[#050510] text-[#E0E0E0] overflow-x-hidden relative font-sans selection:bg-primary/30"
>
	<!-- Background Gradients -->
	<div class="fixed inset-0 z-0 pointer-events-none">
		<div
			class="absolute top-[-10%] left-[-10%] w-[150vw] sm:w-[800px] h-[800px] bg-indigo-600/10 rounded-full blur-[120px] mix-blend-screen opacity-30 animate-pulse"
		/>
		<div
			class="absolute bottom-[-10%] right-[-10%] w-[150vw] sm:w-[600px] h-[600px] bg-fuchsia-600/10 rounded-full blur-[100px] mix-blend-screen opacity-30 animate-pulse"
			style="animation-delay: 2s;"
		/>
	</div>

	<nav
		class="fixed top-0 left-0 w-full z-50 border-b border-white/5 bg-[#050510]/70 backdrop-blur-lg"
	>
		<div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 sm:h-20 flex items-center justify-between">
			<a href={$locale === 'ru' ? '/ru' : '/'} class="flex items-center gap-2 group">
				<img
					src="/logo.svg"
					alt="Logo"
					class="w-8 h-8 sm:w-10 sm:h-10 transition-transform group-hover:scale-110"
				/>
				<span class="text-lg sm:text-xl font-bold tracking-tight text-white">{$t('app_name')}</span>
			</a>
			<div class="flex items-center gap-4 sm:gap-6">
				<a
					href={$locale === 'ru' ? '/ru' : '/'}
					class="text-xs sm:text-sm font-medium text-white/60 hover:text-white transition-colors"
				>
					{$locale === 'ru' ? 'Главная' : 'Home'}
				</a>
				<a href="/auth/login" class="btn btn-primary btn-xs sm:btn-sm rounded-full">
					{$locale === 'ru' ? 'Вход' : 'Login'}
				</a>
			</div>
		</div>
	</nav>

	<main class="relative z-10 pt-24 sm:pt-32 pb-20 sm:pb-32 px-4 sm:px-6">
		<div class="max-w-4xl mx-auto">
			<!-- Header -->
			<header class="mb-16 sm:mb-24 text-center sm:text-left">
				<div
					class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-[10px] sm:text-xs font-medium text-primary mb-6 animate-fade-in-up"
				>
					<span class="relative flex h-2 w-2">
						<span
							class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"
						/>
						<span class="relative inline-flex rounded-full h-2 w-2 bg-primary" />
					</span>
					{$t('changelog_fresh')}
				</div>
				<h1
					class="text-4xl sm:text-6xl md:text-7xl font-bold tracking-tight mb-6 animate-fade-in-up delay-100 leading-tight"
				>
					{#if $locale === 'ru'}
						Эволюция <span
							class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-primary to-fuchsia-400"
							>Скриптуса</span
						>
					{:else}
						The <span
							class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-primary to-fuchsia-400"
							>Evolution</span
						>
					{/if}
				</h1>
				<p
					class="text-base sm:text-xl text-white/50 max-w-2xl animate-fade-in-up delay-200 leading-relaxed"
				>
					{$t('changelog_desc')}
				</p>
			</header>

			<!-- Modern Era Section -->
			<section class="mb-20 sm:mb-32">
				<div class="flex items-center gap-4 mb-12 sm:mb-16">
					<div
						class="h-px flex-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent"
					/>
					<h2
						class="text-xs sm:text-sm font-black uppercase tracking-[0.2em] text-primary/80 whitespace-nowrap bg-[#050510] px-4"
					>
						{$t('changelog_era_modern')}
					</h2>
					<div
						class="h-px flex-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent"
					/>
				</div>

				<div class="relative space-y-12 sm:space-y-24">
					<div
						class="absolute left-0 sm:left-1/2 top-4 bottom-0 w-px bg-gradient-to-b from-primary/40 via-primary/5 to-transparent hidden sm:block"
					/>

					{#each modernUpdates as update, i}
						<div class="relative flex flex-col sm:flex-row items-start gap-6 sm:gap-16 group">
							<div
								class="absolute left-0 sm:left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-primary shadow-[0_0_15px_theme(colors.primary)] z-10 hidden sm:block mt-2"
							/>

							<div
								class="w-full sm:w-1/2 {i % 2 === 0
									? 'sm:text-right sm:pr-12'
									: 'sm:order-last sm:pl-12'} animate-fade-in-up"
								style="animation-delay: {0.3 + i * 0.1}s"
							>
								<div class="space-y-4">
									<div
										class="flex items-center gap-3 {i % 2 === 0
											? 'sm:justify-end'
											: 'sm:justify-start'}"
									>
										<span
											class="text-[10px] sm:text-xs font-mono text-primary font-bold px-2 py-0.5 rounded-md bg-primary/10 border border-primary/20"
											>{update.version}</span
										>
										<span class="w-1 h-1 rounded-full bg-white/20" />
										<time
											class="text-[10px] sm:text-xs text-white/40 font-medium uppercase tracking-widest"
											>{update.date}</time
										>
									</div>
									<h3
										class="text-2xl sm:text-3xl font-bold text-white group-hover:text-primary transition-colors"
									>
										{update.title}
									</h3>
									{#if update.description}
										<p class="text-sm sm:text-base text-white/50 leading-relaxed">
											{update.description}
										</p>
									{/if}
								</div>
							</div>

							<div
								class="w-full sm:w-1/2 {i % 2 === 0 ? 'sm:pl-12' : 'sm:pr-12'} animate-fade-in-up"
								style="animation-delay: {0.4 + i * 0.1}s"
							>
								<div
									class="p-6 sm:p-8 rounded-[2rem] bg-white/5 border border-white/10 backdrop-blur-md hover:border-primary/40 hover:bg-white/[0.08] transition-all group/card relative overflow-hidden"
								>
									{#if update.highlight}
										<div class="absolute top-0 right-0 p-4">
											<span
												class="text-[9px] font-bold px-2 py-0.5 rounded-full bg-primary/20 text-primary border border-primary/20 uppercase tracking-tighter"
												>{$t('changelog_top_story')}</span
											>
										</div>
									{/if}

									<ul class="space-y-3 sm:space-y-4">
										{#each update.changes as change}
											<li class="flex items-start gap-3 group/item">
												<span
													class="mt-1.5 px-1.5 py-0.5 text-[8px] sm:text-[9px] uppercase font-black rounded border {getTagClass(
														change.type
													)} shrink-0 tracking-wider"
												>
													{change.type}
												</span>
												<span
													class="text-xs sm:text-sm text-white/70 group-hover/item:text-white transition-colors leading-relaxed"
												>
													{change.text}
												</span>
											</li>
										{/each}
									</ul>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</section>

			<!-- The Fork / Heritage Section -->
			<section
				class="mb-20 sm:mb-32 relative py-12 px-6 sm:px-12 rounded-[3rem] bg-gradient-to-b from-white/[0.03] to-transparent border border-white/10 overflow-hidden"
			>
				<div
					class="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-primary/20 blur-[100px] rounded-full -translate-y-1/2"
				/>
				<div class="relative z-10 text-center max-w-2xl mx-auto space-y-6">
					<div class="flex justify-center -space-x-4 mb-4">
						<div
							class="w-12 h-12 rounded-full border-2 border-[#050510] bg-white/10 flex items-center justify-center backdrop-blur-sm grayscale opacity-50"
						>
							<svg class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor"
								><path
									d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.04-1.341-3.364-1.238L5.61 16.71c-.244-.132-.5-.316-.5-.316.48-.007.828.441.828.441.442.756 1.159.537 1.441.411.045-.321.173-.538.316-.662-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.137 20.161 22 16.416 22 12c0-5.523-4.477-10-10-10z"
								/></svg
							>
						</div>
						<div
							class="w-12 h-12 rounded-full border-2 border-[#050510] bg-primary flex items-center justify-center shadow-lg shadow-primary/20"
						>
							<img src="/logo.svg" class="w-7 h-7" alt="Scriptus" />
						</div>
					</div>
					<h2 class="text-2xl sm:text-3xl font-bold">The Great Fork</h2>
					<p class="text-white/40 text-sm sm:text-base leading-relaxed">
						{$t('changelog_fork_notice')}
					</p>
					<div
						class="inline-flex items-center gap-2 text-[10px] font-bold text-white/30 uppercase tracking-[0.3em]"
					>
						<span class="w-8 h-px bg-white/10" />
						Transition Period
						<span class="w-8 h-px bg-white/10" />
					</div>
				</div>
			</section>

			<!-- Legacy Era Section -->
			<section class="opacity-50 hover:opacity-100 transition-opacity duration-500">
				<div class="flex items-center gap-4 mb-12 sm:mb-16">
					<div class="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
					<h2
						class="text-[10px] sm:text-xs font-black uppercase tracking-[0.2em] text-white/40 whitespace-nowrap bg-[#050510] px-4"
					>
						{$t('changelog_era_legacy')}
					</h2>
					<div class="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
				</div>

				<div class="relative space-y-10 sm:space-y-16">
					<div class="absolute left-0 sm:left-1/2 top-4 bottom-0 w-px bg-white/5 hidden sm:block" />

					{#each legacyUpdates as update, i}
						<div
							class="relative flex flex-col sm:flex-row items-start gap-4 sm:gap-12 group/legacy"
						>
							<div
								class="absolute left-0 sm:left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-white/20 z-10 hidden sm:block mt-2 group-hover/legacy:bg-white/40 transition-colors"
							/>

							<div
								class="w-full sm:w-1/2 {i % 2 === 0
									? 'sm:text-right sm:pr-10'
									: 'sm:order-last sm:pl-10'}"
							>
								<div class="space-y-2">
									<div
										class="flex items-center gap-3 {i % 2 === 0
											? 'sm:justify-end'
											: 'sm:justify-start'}"
									>
										<span
											class="text-[9px] font-mono text-white/30 font-bold px-1.5 py-0.5 rounded border border-white/10"
											>{update.version}</span
										>
										<time class="text-[9px] text-white/20 font-medium tracking-wider"
											>{update.date}</time
										>
									</div>
									<h4
										class="text-lg sm:text-xl font-bold text-white/60 group-hover/legacy:text-white/80 transition-colors"
									>
										{update.title}
									</h4>
								</div>
							</div>

							<div class="w-full sm:w-1/2 {i % 2 === 0 ? 'sm:pl-10' : 'sm:pr-10'}">
								<div
									class="p-4 sm:p-6 rounded-2xl bg-white/[0.02] border border-white/5 group-hover/legacy:border-white/10 transition-all"
								>
									<ul class="space-y-2">
										{#each update.changes as change}
											<li class="flex items-start gap-2 text-left">
												<span class="mt-2 w-1 h-1 rounded-full bg-white/20 shrink-0" />
												<span class="text-[11px] sm:text-xs text-white/40 leading-relaxed">
													{change.text}
												</span>
											</li>
										{/each}
									</ul>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</section>

			<!-- Footer Call to Action -->
			<div
				class="mt-32 text-center p-8 sm:p-16 rounded-[4rem] bg-gradient-to-tr from-primary/20 via-indigo-500/10 to-transparent border border-white/10 animate-fade-in-up"
			>
				<h3 class="text-3xl sm:text-4xl font-bold mb-6">
					{$locale === 'ru' ? 'Сделано для творцов.' : 'Built for Creators.'}
				</h3>
				<p class="text-base sm:text-lg text-white/50 mb-10 max-w-sm mx-auto leading-relaxed">
					{$locale === 'ru'
						? 'Присоединяйтесь к тысячам пользователей, которые уже экономят часы на транскрибации каждую неделю.'
						: 'Join thousands of users who are already saving hours on transcription every week.'}
				</p>
				<div class="flex flex-col sm:flex-row gap-4 justify-center">
					<a
						href="/auth/register"
						class="btn btn-primary btn-lg rounded-full px-12 h-14 min-h-[3.5rem] shadow-[0_10px_30px_-5px_theme(colors.primary)]"
						>{$t('start_free')}</a
					>
					<a
						href="https://github.com/pluja/whishper"
						target="_blank"
						class="btn btn-ghost btn-lg rounded-full border border-white/10 h-14 min-h-[3.5rem] px-8"
						>GitHub Heritage</a
					>
				</div>
			</div>
		</div>
	</main>

	<footer
		class="max-w-7xl mx-auto py-12 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-6 px-6 text-center sm:text-left"
	>
		<div class="text-white/30 text-[11px] sm:text-xs uppercase tracking-widest font-medium">
			© 2026 {$t('app_name')}. Crafting precision.
		</div>
		<div
			class="flex gap-8 text-[11px] sm:text-xs uppercase tracking-widest font-bold text-white/30"
		>
			<a href={$locale === 'ru' ? '/ru' : '/'} class="hover:text-primary transition-colors"
				>{$locale === 'ru' ? 'Главная' : 'Home'}</a
			>
			<a href="/changelog#" class="hover:text-primary transition-colors">{$t('privacy')}</a>
			<a href="/changelog#" class="hover:text-primary transition-colors">{$t('terms')}</a>
		</div>
	</footer>
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

	:global(html) {
		scroll-behavior: smooth;
	}

	/* Hide scrollbar but keep functionality */
	.selection\:bg-primary\/30::selection {
		background-color: rgba(99, 102, 241, 0.3);
	}
</style>
