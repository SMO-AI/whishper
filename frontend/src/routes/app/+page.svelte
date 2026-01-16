<script>
	import { Toaster } from 'svelte-french-toast';
	import { transcriptions, uploadProgress } from '$lib/stores';
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
	import { theme } from '$lib/stores';

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
		if (!browser) {
			console.log('Server, not connecting');
			return;
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
		console.log('Connecting to: ', new_uri);
		socket = new WebSocket(new_uri);

		socket.onopen = () => console.log('WebSocket is connected...');
		socket.onerror = (error) => console.log('WebSocket Error: ', error);
		socket.onclose = (event) => {
			console.log('WebSocket is closed with code: ', event.code, ' and reason: ', event.reason);
			setTimeout(() => {
				console.log('Reconnecting...');
				connect(token);
			}, 1000);
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
</script>

<Toaster />
<ModalDownloadOptions tr={downloadTranscription} />
<ModalTranslationForm tr={translateTranscription} />
<ModalTranscriptionForm />
<ModalSubscription bind:this={modalSubscription} />

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
					<button class="justify-between">
						Edit Profile
						<span class="badge badge-sm badge-ghost">New</span>
					</button>
				</li>
				<li><button>Settings</button></li>
				<li><button on:click={() => modalSubscription.showModal()}>Check Subscription</button></li>
				<div class="divider my-0" />
				<li>
					<button class="text-error font-medium hover:bg-error/10" on:click={handleLogout}
						>Logout</button
					>
				</li>
			</ul>
		</div>
	</div>
	<div class="flex flex-col items-center justify-center space-y-4">
		<div class="relative group">
			<div
				class="absolute -inset-1 bg-gradient-to-r from-primary to-secondary rounded-full blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"
			/>
			<img class="relative w-24 h-24" src="/logo.svg" alt="Logo: a cloud whispering" />
		</div>
		<h1
			class="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary"
		>
			Whishper
		</h1>
		<h2 class="font-mono text-center text-md opacity-60 max-w-md italic leading-relaxed px-4">
			"{data.randomSentence}"
		</h2>
	</div>
</header>

<main class="w-full max-w-5xl mx-auto px-4 mb-24">
	<div
		class="bg-base-200/50 backdrop-blur-sm rounded-3xl border border-base-300 p-6 md:p-8 shadow-2xl"
	>
		<div
			class="flex flex-col md:flex-row items-center justify-between gap-6 mb-8 pb-8 border-b border-base-content/10"
		>
			<div class="text-center md:text-left">
				<h3 class="text-2xl font-bold tracking-tight">Your Library</h3>
				<p class="text-sm opacity-60">Manage and explore your transcriptions</p>
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
							>Uploading {$uploadProgress}%</span
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
						✨ New Transcription
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
						Your collection is empty
					</p>
					<p class="text-sm">Start by uploading your first audio file</p>
				</div>
			{/if}
		</div>
	</div>
</main>
