<script>
	import { theme, t } from '$lib/stores';

	// Animation constants or states could go here
</script>

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
			<a href="/ru" class="flex items-center gap-2 group cursor-pointer">
				<img
					src="/logo.svg"
					alt="App Logo"
					class="w-10 h-10 transition-transform group-hover:scale-110"
				/>
				<span
					class="text-xl font-bold tracking-tight text-white group-hover:opacity-80 transition-opacity"
					>{$t('app_name')}</span
				>
			</a>

			<!-- Desktop Nav Elements (Optional) -->
			<div class="hidden md:flex items-center gap-8 text-sm font-medium text-white/60">
				<a href="#features" class="hover:text-white transition-colors">Функции</a>
				<a href="#pricing" class="hover:text-white transition-colors">Цены</a>
				<a href="#testimonials" class="hover:text-white transition-colors">Отзывы</a>
			</div>

			<!-- CTA -->
			<div class="flex items-center gap-4">
				<a
					href="/auth/login"
					class="text-sm font-medium text-white/70 hover:text-white transition-colors hidden md:block"
					>Войти</a
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
						>Начать</span
					>
					<span class="relative invisible">Начать</span>
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
				Транскрипция нового поколения уже здесь
			</div>

			<h1
				class="text-5xl md:text-8xl font-bold tracking-tight mb-8 leading-[1.1] animate-fade-in-up delay-100"
			>
				Ваш Голос, <br />
				<span
					class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-primary to-fuchsia-400"
				>
					Идеально Записанный.
				</span>
			</h1>

			<p
				class="text-lg md:text-xl text-white/50 max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up delay-200"
			>
				Превращайте аудио в безупречный текст с помощью самых передовых моделей ИИ.
				<span class="text-white/80">Whisper V3 Turbo</span> обеспечивает точность 99.9% с молниеносной
				скоростью.
			</p>

			<div class="flex flex-col sm:flex-row items-center gap-4 animate-fade-in-up delay-300">
				<a
					href="/auth/register"
					class="btn btn-primary btn-lg rounded-full px-10 shadow-[0_0_30px_-5px_theme(colors.primary)] hover:shadow-[0_0_50px_-5px_theme(colors.primary)] border-none text-white transition-all hover:scale-105"
				>
					Начать Бесплатно
				</a>
				<a
					href="/auth/login"
					class="btn btn-ghost btn-lg rounded-full px-8 text-white/60 hover:text-white hover:bg-white/5 border border-white/5 hover:border-white/20 flex items-center justify-center"
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
								Перетащите файл сюда или нажмите
							</p>
							<p class="text-sm text-white/40">Поддерживаемые форматы: MP3, WAV, M4A, MP4</p>
						</div>

						<!-- Fake Progress/Status Pill -->
						<div
							class="inline-flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/5 text-xs text-white/30 mt-4"
						>
							<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
							Готов к обработке
						</div>
					</div>
				</a>
			</div>
		</section>

		<!-- Features Bento Grid -->
		<section id="features" class="max-w-7xl mx-auto mb-32">
			<div class="text-center mb-16">
				<h2 class="text-3xl md:text-5xl font-bold mb-4">
					Всё, что вам нужно. <br /><span class="text-white/40">И ничего лишнего.</span>
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
					<h3 class="text-2xl font-bold mb-2">Молниеносно быстро</h3>
					<p class="text-white/60 text-lg max-w-md">
						Обрабатывайте часы аудио за минуты. Наш оптимизированный движок работает до 10 раз
						быстрее воспроизведения.
					</p>
					<div class="mt-8 flex items-end gap-2 text-4xl font-mono text-primary">
						10x <span class="text-sm text-white/40 mb-2 font-sans">Быстрее</span>
					</div>
				</div>

				<!-- Accuracy Card -->
				<div
					class="md:col-span-2 rounded-3xl p-8 bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-primary/30 transition-colors flex flex-col justify-between"
				>
					<div>
						<h3 class="text-2xl font-bold mb-2">Точность</h3>
						<p class="text-white/60">На базе Whisper V3.</p>
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
					<h3 class="text-xl font-bold mb-2">Приватность</h3>
					<p class="text-white/60 text-sm">
						Ваши данные зашифрованы. Мы не обучаем модели на ваших файлах.
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
							RU
						</div>
						<div
							class="w-10 h-10 rounded-full border-2 border-[#050510] bg-white/20 flex items-center justify-center text-xs"
						>
							+90
						</div>
					</div>
					<h3 class="text-xl font-bold">Мультиязычность</h3>
					<p class="text-white/60 text-sm mt-2">Поддержка более 90 языков.</p>
				</div>

				<!-- Editor Card -->
				<div
					class="md:col-span-2 rounded-3xl p-8 bg-white/5 border border-white/10 hover:border-primary/30 transition-colors group"
				>
					<h3 class="text-xl font-bold mb-2">Умный Редактор</h3>
					<p class="text-white/60 text-sm mb-4">
						Удобное редактирование, таймкоды, разделение спикеров и экспорт.
					</p>
					<div class="w-full h-2 rounded bg-white/10 overflow-hidden">
						<div
							class="w-2/3 h-full bg-primary/50 group-hover:w-full transition-all duration-1000"
						/>
					</div>
				</div>
			</div>
		</section>

		<!-- Footer -->
		<footer
			class="max-w-7xl mx-auto pt-20 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6"
		>
			<div class="text-white/40 text-sm">© 2026 {$t('app_name')}. Все права защищены.</div>
			<div class="flex gap-6 text-sm text-white/40">
				<a href="#" class="hover:text-white transition-colors">Конфиденциальность</a>
				<a href="#" class="hover:text-white transition-colors">Условия</a>
				<a href="#" class="hover:text-white transition-colors">Контакты</a>
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
