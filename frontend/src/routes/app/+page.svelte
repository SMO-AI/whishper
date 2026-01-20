<script>
	import { Toaster } from 'svelte-french-toast';
	import { transcriptions, uploadProgress, theme, locale, t } from '$lib/stores';
	import { browser, dev } from '$app/environment';
	import { CLIENT_WS_HOST } from '$lib/utils';
	import { onMount, onDestroy } from 'svelte';
	import ModalTranscriptionForm from '$lib/components/ModalTranscriptionForm.svelte';
	import ModalDownloadOptions from '$lib/components/ModalDownloadOptions.svelte';
	import ModalTranslationForm from '$lib/components/ModalTranslationForm.svelte';
	import SuccessTranscription from '$lib/components/SuccessTranscription.svelte';
	import PendingTranscription from '$lib/components/PendingTranscription.svelte';
	import PendingTranslation from '$lib/components/PendingTranslation.svelte';
	import ErrorTranscription from '$lib/components/ErrorTranscription.svelte';
	import ModalSubscription from '$lib/components/ModalSubscription.svelte';
	import ModalSettings from '$lib/components/ModalSettings.svelte';
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';

	const toggleTheme = () => {
		theme.update((t) => (t === 'light' ? 'dark' : 'light'));
	};

	async function handleLogout() {
		await supabase.auth.signOut();
		goto('/auth/login');
	}

	//export let data;
	let socket;
	export let data;

	function connect(token) {
		if (!browser) return;

		// Close existing socket if any
		if (socket) {
			console.log('Closing existing socket...');
			socket.onclose = null; // Prevent reconnection loop from old socket
			socket.close();
		}

		let new_uri = '';
		var loc = window.location;
		if (loc.protocol === 'https:') {
			new_uri = 'wss:';
		} else {
			new_uri = 'ws:';
		}
		new_uri += '//' + (CLIENT_WS_HOST == '' ? loc.host : CLIENT_WS_HOST);
		new_uri += '/ws/transcriptions?token=' + token;

		console.log('Connecting to WebSocket...');
		socket = new WebSocket(new_uri);

		socket.onopen = () => console.log('WebSocket connected');
		socket.onerror = (error) => console.log('WebSocket connection error');
		socket.onclose = (event) => {
			if (event.code !== 1000) {
				console.log(`WebSocket closed (code: ${event.code}). Reconnecting...`);
				setTimeout(() => connect(token), 3000);
			} else {
				console.log('WebSocket closed normally');
			}
		};

		socket.onmessage = (event) => {
			let update = JSON.parse(event.data);
			// use update to update the store
			transcriptions.update((transcriptions) => {
				let index = transcriptions.findIndex((tr) => tr.id === update.id);
				if (index >= 0) {
					// replace the item at index
					transcriptions[index] = update;
				} else {
					// add the new item
					transcriptions.push(update);
				}
				return transcriptions; // return a new object to trigger reactivity
			});
		};
	}

	onMount(async () => {
		const {
			data: { session }
		} = await supabase.auth.getSession();
		if (!session) {
			goto('/auth/login');
			return;
		}

		// Ensure user has the correct app metadata (e.g. for Google Login)
		const appMeta = session.user.user_metadata?.app;
		if (appMeta !== 'Scriptus' && appMeta !== 'whishper') {
			console.log('Updating user metadata to Scriptus...');
			await supabase.auth.updateUser({
				data: { app: 'Scriptus' }
			});
		}

		connect(session.access_token);
	});

	let downloadTranscription = null;
	let handleDownload = (event) => {
		downloadTranscription = event.detail; // this will be the transcription to download
		modalDownloadOptions.showModal(); // show the modal
	};
	let translateTranscription = null;
	let handleTranslate = (event) => {
		translateTranscription = event.detail; // this will be the transcription to translate
		modalTranslation.showModal(); // show the modal
	};

	onDestroy(() => {
		if (socket) {
			socket.close(1000);
		}
	});
	let modalSubscription;
	let modalSettings;

	let cloudAnimation = '';
	const cloudAnimations = [
		'animate-cloud-bounce',
		'animate-cloud-shake',
		'animate-cloud-spin',
		'animate-cloud-pulse',
		'animate-cloud-wobble',
		'animate-cloud-rubber',
		'animate-cloud-tada',
		'animate-cloud-jello'
	];
	let lastAnimationIndex = -1;

	function triggerCloudAnimation() {
		// Log for verification
		console.log('☁️ Cloud animation triggered!');

		// If already animating, don't trigger another one
		if (cloudAnimation) return;

		let index;
		do {
			index = Math.floor(Math.random() * cloudAnimations.length);
		} while (index === lastAnimationIndex);

		lastAnimationIndex = index;
		cloudAnimation = cloudAnimations[index];

		// Reset animation class after completion to allow re-triggering
		setTimeout(() => {
			cloudAnimation = '';
		}, 1000);
	}

	let modalTranscriptionForm;
	let isDraggingGlobal = false;

	function handleDragOverGlobal(e) {
		e.preventDefault();
		isDraggingGlobal = true;
	}

	function handleDragLeaveGlobal(e) {
		e.preventDefault();
		if (!e.currentTarget.contains(e.relatedTarget)) {
			isDraggingGlobal = false;
		}
	}

	function handleDropGlobal(e) {
		e.preventDefault();
		isDraggingGlobal = false;
		if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
			modalTranscriptionForm.handleFiles(e.dataTransfer.files);
		}
	}
</script>

<Toaster />
<ModalDownloadOptions tr={downloadTranscription} />
<ModalTranslationForm tr={translateTranscription} />
<ModalTranscriptionForm bind:this={modalTranscriptionForm} />
<ModalSubscription bind:this={modalSubscription} />
<ModalSettings bind:this={modalSettings} />

<header class="py-12 bg-gradient-to-b from-primary/5 to-transparent relative">
	<div class="absolute top-4 right-4 md:top-8 md:right-8 flex items-center gap-2">
		<button
			on:click={toggleTheme}
			class="btn btn-circle btn-ghost transition-all duration-300 hover:rotate-12"
			aria-label="Toggle Theme"
		>
			{#if $theme === 'light'}
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-6 h-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
					/></svg
				>
			{:else}
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-6 h-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
					/></svg
				>
			{/if}
		</button>

		<div class="dropdown dropdown-end">
			<div tabindex="0" role="button" class="btn btn-circle btn-ghost transition-all duration-300">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-6 h-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
					/>
				</svg>
			</div>
			<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
			<ul
				tabindex="0"
				class="dropdown-content z-[1] menu p-2 shadow-lg bg-base-100 rounded-box w-52 mt-4 border border-base-200"
			>
				<li>
					<button on:click={() => modalSettings.showModal('profile')}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-5 h-5 opacity-60"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
							/><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
							/></svg
						>
						{$t('settings')}
					</button>
				</li>
				<li>
					<button on:click={() => modalSubscription.showModal()}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-5 h-5 opacity-60"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
							/></svg
						>
						{$t('check_subscription')}
					</button>
				</li>
				<div class="divider my-0" />
				<li>
					<button class="text-error font-medium hover:bg-error/10" on:click={handleLogout}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-5 h-5"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
							/></svg
						>
						{$t('logout')}
					</button>
				</li>
			</ul>
		</div>
	</div>
	<div class="flex flex-col items-center justify-center space-y-4">
		<button
			on:click={triggerCloudAnimation}
			class="relative group focus:outline-none transition-transform active:scale-95 z-20"
			aria-label="Click for a surprise"
		>
			<div
				class="absolute -inset-2 bg-gradient-to-r from-primary to-secondary rounded-full blur opacity-25 group-hover:opacity-60 transition duration-1000 group-hover:duration-200"
			/>
			<img
				class="relative w-24 h-24 cursor-pointer select-none transition-all duration-300 hover:scale-110 {cloudAnimation}"
				src="/logo.svg"
				alt="Logo: a cloud whispering"
			/>
		</button>
		<h1
			class="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary"
		>
			{$t('app_name')}
		</h1>
		<h2 class="font-mono text-center text-md opacity-60 max-w-md italic leading-relaxed px-4">
			"{$t(data.randomSentence)}"
		</h2>
	</div>
</header>

<main class="w-full max-w-5xl mx-auto px-4 mb-24">
	<div
		role="region"
		aria-label="Transcription Library and Drop Zone"
		class="bg-base-200/50 backdrop-blur-sm rounded-3xl border-2 border-dashed p-6 md:p-8 shadow-2xl transition-all duration-300 {isDraggingGlobal
			? 'border-primary bg-primary/5 ring-8 ring-primary/5'
			: 'border-base-300'}"
		on:dragover={handleDragOverGlobal}
		on:dragleave={handleDragLeaveGlobal}
		on:drop={handleDropGlobal}
	>
		<div
			class="flex flex-col md:flex-row items-center justify-between gap-6 mb-8 pb-8 border-b border-base-content/10"
		>
			<div class="text-center md:text-left">
				<h3 class="text-2xl font-bold tracking-tight">{$t('your_library')}</h3>
				<p class="text-sm opacity-60">{$t('manage_explore')}</p>
			</div>

			<div class="flex items-center gap-4">
				{#if $uploadProgress > 0}
					<div class="flex flex-col items-end min-w-[200px]">
						<progress
							class="progress progress-primary w-full h-3"
							value={$uploadProgress}
							max="100"
						/>
						<span
							class="text-[10px] uppercase font-bold tracking-widest mt-1 opacity-60 animate-pulse"
							>{$t('uploading')} {$uploadProgress}%</span
						>
					</div>
				{:else}
					<button
						class="btn btn-primary btn-md md:btn-lg px-8 rounded-2xl shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all font-bold group"
						onclick="modalNewTranscription.showModal()"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-5 h-5 group-hover:rotate-90 transition-transform duration-300"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="3"
							stroke-linecap="round"
							stroke-linejoin="round"
							><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg
						>
						✨ {$t('new_transcription')}
					</button>
				{/if}
			</div>
		</div>

		<div class="flex flex-col space-y-1">
			{#if $transcriptions.length > 0}
				{#each $transcriptions.slice().reverse() as tr (tr.id)}
					{#if tr.status == 2}
						<SuccessTranscription
							{tr}
							on:download={handleDownload}
							on:translate={handleTranslate}
						/>
					{/if}
					{#if tr.status < 2 && tr.status >= 0}
						<PendingTranscription {tr} />
					{/if}
					{#if tr.status == 3}
						<PendingTranslation {tr} />
					{/if}
					{#if tr.status < 0}
						<ErrorTranscription {tr} />
					{/if}
				{/each}
			{:else}
				<div class="py-20 flex flex-col items-center justify-center opacity-40">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-24 h-24 mb-4"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1"
						stroke-linecap="round"
						stroke-linejoin="round"
						><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg
					>
					<p class="text-2xl font-bold text-center tracking-tight italic">
						{$t('collection_empty')}
					</p>
					<p class="text-sm">{$t('start_uploading')}</p>
				</div>
			{/if}
		</div>
	</div>
</main>

<style>
	/* Cloud Animations (Global to support dynamic class names) */
	:global(.animate-cloud-bounce) {
		animation: cloud-bounce 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
	}

	/* Subtle float animation on hover */
	.group:hover img:not([class*='animate-cloud-']) {
		animation: cloud-float 3s ease-in-out infinite;
	}

	@keyframes cloud-float {
		0%,
		100% {
			transform: translateY(0) rotate(0deg);
		}
		25% {
			transform: translateY(-4px) rotate(1deg);
		}
		75% {
			transform: translateY(-2px) rotate(-1deg);
		}
	}

	:global(.animate-cloud-shake) {
		animation: cloud-shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
	}
	:global(.animate-cloud-spin) {
		animation: cloud-spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) both;
	}
	:global(.animate-cloud-pulse) {
		animation: cloud-pulse 0.5s ease-in-out both;
	}
	:global(.animate-cloud-wobble) {
		animation: cloud-wobble 0.8s ease-in-out both;
	}
	:global(.animate-cloud-rubber) {
		animation: cloud-rubber 0.8s ease-in-out both;
	}
	:global(.animate-cloud-tada) {
		animation: cloud-tada 0.8s ease-in-out both;
	}
	:global(.animate-cloud-jello) {
		animation: cloud-jello 0.8s ease-in-out both;
	}

	@keyframes cloud-bounce {
		0%,
		20%,
		50%,
		80%,
		100% {
			transform: translateY(0);
		}
		40% {
			transform: translateY(-30px) scaleY(1.1);
		}
		60% {
			transform: translateY(-15px) scaleY(1.05);
		}
	}

	@keyframes cloud-shake {
		10%,
		90% {
			transform: translate3d(-1px, 0, 0);
		}
		20%,
		80% {
			transform: translate3d(2px, 0, 0);
		}
		30%,
		50%,
		70% {
			transform: translate3d(-4px, 0, 0);
		}
		40%,
		60% {
			transform: translate3d(4px, 0, 0);
		}
	}

	@keyframes cloud-spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	@keyframes cloud-pulse {
		0% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.3);
			filter: brightness(1.2);
		}
		100% {
			transform: scale(1);
		}
	}

	@keyframes cloud-wobble {
		0% {
			transform: translateX(0%);
		}
		15% {
			transform: translateX(-25%) rotate(-5deg);
		}
		30% {
			transform: translateX(20%) rotate(3deg);
		}
		45% {
			transform: translateX(-15%) rotate(-3deg);
		}
		60% {
			transform: translateX(10%) rotate(2deg);
		}
		75% {
			transform: translateX(-5%) rotate(-1deg);
		}
		100% {
			transform: translateX(0%);
		}
	}

	@keyframes cloud-rubber {
		0% {
			transform: scale3d(1, 1, 1);
		}
		30% {
			transform: scale3d(1.25, 0.75, 1);
		}
		40% {
			transform: scale3d(0.75, 1.25, 1);
		}
		50% {
			transform: scale3d(1.15, 0.85, 1);
		}
		65% {
			transform: scale3d(0.95, 1.05, 1);
		}
		75% {
			transform: scale3d(1.05, 0.95, 1);
		}
		100% {
			transform: scale3d(1, 1, 1);
		}
	}

	@keyframes cloud-tada {
		0% {
			transform: scale3d(1, 1, 1);
		}
		10%,
		20% {
			transform: scale3d(0.9, 0.9, 0.9) rotate3d(0, 0, 1, -3deg);
		}
		30%,
		50%,
		70%,
		90% {
			transform: scale3d(1.1, 1.1, 1.1) rotate3d(0, 0, 1, 3deg);
		}
		40%,
		60%,
		80% {
			transform: scale3d(1.1, 1.1, 1.1) rotate3d(0, 0, 1, -3deg);
		}
		100% {
			transform: scale3d(1, 1, 1);
		}
	}

	@keyframes cloud-jello {
		11.1% {
			transform: skewX(-12.5deg) skewY(-12.5deg);
		}
		22.2% {
			transform: skewX(6.25deg) skewY(6.25deg);
		}
		33.3% {
			transform: skewX(-3.125deg) skewY(-3.125deg);
		}
		44.4% {
			transform: skewX(1.5625deg) skewY(1.5625deg);
		}
		55.5% {
			transform: skewX(-0.78125deg) skewY(-0.78125deg);
		}
		66.6% {
			transform: skewX(0.390625deg) skewY(0.390625deg);
		}
		77.7% {
			transform: skewX(-0.1953125deg) skewY(-0.1953125deg);
		}
		88.8% {
			transform: skewX(0.09765625deg) skewY(0.09765625deg);
		}
		100% {
			transform: skewX(0) skewY(0);
		}
	}
</style>
