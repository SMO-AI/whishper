<script>
	/** @type {import('./$types').PageData} */
	import toast, { Toaster } from 'svelte-french-toast';
	import Editor from '$lib/components/Editor.svelte';
	import { currentVideoPlayerTime, currentTranscription } from '$lib/stores';
	import { CLIENT_API_HOST } from '$lib/utils';

	let video;
	let tolerance = 0.1; // Tolerance level in seconds
	let canPlay = false;

	export let data;
	$: if (data?.transcription) {
		currentTranscription.set(data.transcription);
	}

	$: if (canPlay && video && Math.abs(video.currentTime - $currentVideoPlayerTime) > tolerance) {
		console.log(video.currentTime, $currentVideoPlayerTime);
		// When testing in Chrome, it works, just see https://stackoverflow.com/a/67584611
		video.currentTime = $currentVideoPlayerTime;
	}
</script>

<Toaster />
{#if $currentTranscription}
	<div class="flex flex-col h-[100dvh] lg:grid lg:grid-cols-3 overflow-hidden">
		<div class="w-full shrink-0 lg:col-span-1 lg:h-full bg-black relative shadow-lg z-20">
			<div class="relative w-full h-[30vh] lg:h-full bg-black flex items-center justify-center">
				<video
					id="video"
					controls
					playsinline
					bind:this={video}
					on:timeupdate={(e) => ($currentVideoPlayerTime = e.target.currentTime)}
					on:canplay={() => (canPlay = true)}
					on:loadedmetadata={() => (canPlay = true)}
					class="w-full h-full object-contain"
				>
					<source
						src="{CLIENT_API_HOST}/api/video/{$currentTranscription.fileName}"
						type="video/mp4"
					/>
					<track kind="captions" />
				</video>
			</div>
		</div>
		<div class="flex-1 w-full overflow-hidden bg-base-100 lg:col-span-2 relative z-10">
			<Editor />
		</div>
	</div>
{:else}
	<div class="flex items-center justify-center w-screen h-screen">
		<h1>
			<span class="loading loading-bars loading-lg" />
		</h1>
	</div>
{/if}
