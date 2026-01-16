<script>
	/** @type {import('./$types').PageData} */
	import toast, { Toaster } from 'svelte-french-toast';
	import Editor from '$lib/components/Editor.svelte';
	import { currentVideoPlayerTime, currentTranscription } from '$lib/stores';
	import { CLIENT_API_HOST } from '$lib/utils';
	import { fade, fly } from 'svelte/transition';

	let video;
	let tolerance = 0.1; // Tolerance level in seconds
	let canPlay = false;

	// Media State
	let videoWidth = 0;
	let videoHeight = 0;
	$: isVertical = videoHeight > videoWidth;
	$: aspectRatio = videoWidth && videoHeight ? videoWidth / videoHeight : 16 / 9;

	export let data;
	$: if (data?.transcription) {
		currentTranscription.set(data.transcription);
	}

	// Determine if the file is likely audio based on extension
	const audioExtensions = ['mp3', 'wav', 'm4a', 'flac', 'aac', 'ogg', 'wma', 'aiff'];
	$: isAudio = $currentTranscription?.fileName
		? audioExtensions.some((ext) =>
				$currentTranscription.fileName.toLowerCase().endsWith('.' + ext)
		  )
		: false;

	// Sync logic
	$: if (canPlay && video && Math.abs(video.currentTime - $currentVideoPlayerTime) > tolerance) {
		video.currentTime = $currentVideoPlayerTime;
	}
</script>

<Toaster />

{#if $currentTranscription}
	<div class="flex flex-col h-[100dvh] bg-base-100 overflow-hidden lg:flex-row">
		<!-- Media Player Section -->
		<div
			class="relative z-20 shrink-0 shadow-xl transition-all duration-500 ease-spring
            {isAudio
				? 'w-full bg-base-100 border-b border-base-200'
				: 'bg-black flex items-center justify-center ' +
				  (isVertical
						? 'h-[40vh] lg:h-full lg:w-[25vw] xl:w-[20vw]'
						: 'h-[35vh] lg:h-full lg:w-[40vw] xl:w-[35vw]')}"
		>
			{#if isAudio}
				<!-- AUDIO PLAYER DESIGN -->
				<div
					class="w-full p-3 md:p-4 flex items-center justify-center bg-base-100/80 backdrop-blur-md"
				>
					<div
						class="w-full max-w-3xl bg-base-200/50 rounded-2xl border border-base-content/5 p-2 pr-4 flex items-center gap-4 shadow-sm"
					>
						<div
							class="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="w-5 h-5 md:w-6 md:h-6"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path d="M9 18V5l12-2v13" /><circle cx="6" cy="18" r="3" /><circle
									cx="18"
									cy="16"
									r="3"
								/>
							</svg>
						</div>
						<!-- Native Audio with custom CSS to make it sleek -->
						<audio
							bind:this={video}
							on:timeupdate={(e) => ($currentVideoPlayerTime = e.target.currentTime)}
							on:canplay={() => (canPlay = true)}
							on:loadedmetadata={() => (canPlay = true)}
							controls
							class="w-full h-8 md:h-10 focus:outline-none opacity-80 hover:opacity-100 transition-opacity"
						>
							<source
								src="{CLIENT_API_HOST}/api/video/{$currentTranscription.fileName}"
								type="audio/mp4"
							/>
							Your browser does not support the audio element.
						</audio>
					</div>
				</div>
			{:else}
				<!-- VIDEO PLAYER DESIGN -->
				<div class="relative w-full h-full flex items-center justify-center overflow-hidden">
					<!-- Ambient Background -->
					<div
						class="absolute inset-0 bg-gradient-to-br from-base-300/10 to-base-100/5 backdrop-blur-3xl z-0"
					/>

					<video
						id="video"
						bind:this={video}
						bind:videoWidth
						bind:videoHeight
						on:timeupdate={(e) => ($currentVideoPlayerTime = e.target.currentTime)}
						on:canplay={() => (canPlay = true)}
						on:loadedmetadata={() => (canPlay = true)}
						controls
						playsinline
						class="relative z-10 w-full h-full shadow-2xl {isVertical
							? 'object-contain px-4 py-2'
							: 'object-contain'}"
					>
						<source
							src="{CLIENT_API_HOST}/api/video/{$currentTranscription.fileName}"
							type="video/mp4"
						/>
						<track kind="captions" />
					</video>
				</div>
			{/if}
		</div>

		<!-- Editor Section -->
		<div class="flex-1 h-full overflow-hidden bg-base-100 relative z-10 flex flex-col">
			<Editor />
		</div>
	</div>
{:else if data?.error}
	<div class="flex flex-col items-center justify-center min-h-screen gap-4">
		<div
			class="p-8 bg-error/5 text-error rounded-3xl border border-error/20 flex flex-col items-center gap-4 max-w-md text-center"
		>
			<div class="w-16 h-16 rounded-full bg-error/10 flex items-center justify-center">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-8 h-8"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
					/>
				</svg>
			</div>
			<div>
				<h2 class="text-2xl font-bold mb-1 tracking-tight">{data.error}</h2>
				<p class="opacity-70 text-sm">
					We couldn't open the editor for this transcription. Please verify you're logged in and
					have access.
				</p>
			</div>
			<a href="/app" class="btn btn-error btn-outline btn-sm rounded-xl px-6">Return to App</a>
		</div>
	</div>
{:else}
	<div class="flex items-center justify-center w-screen h-screen">
		<span class="loading loading-dots loading-lg text-primary" />
	</div>
{/if}

<style>
	/* Custom styling for audio element to make it fit the theme better */
	audio::-webkit-media-controls-panel {
		background-color: transparent;
	}
</style>
