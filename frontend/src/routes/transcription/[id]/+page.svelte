<script>
	import { currentTranscription } from '$lib/stores';
	import toast, { Toaster } from 'svelte-french-toast';
	import { fade } from 'svelte/transition';
	import { onMount } from 'svelte';
	import { CLIENT_API_HOST } from '$lib/utils';

	let showTimestamps = false;
	let transcriptionText = '';

	// Helpers for formatting
	const formatTime = (seconds) => {
		return new Date(seconds * 1000).toISOString().substr(11, 8);
	};

	const formatDate = (id) => {
		if (!id) return 'Unknown';
		return new Date(parseInt(id.substring(0, 8), 16) * 1000).toLocaleString();
	};

	// Reactive text generation based on toggle
	$: if ($currentTranscription) {
		if (showTimestamps) {
			transcriptionText = $currentTranscription.result.segments
				.map((s) => `[${formatTime(s.start)} - ${formatTime(s.end)}] ${s.text.trim()}`)
				.join('\n');
		} else {
			transcriptionText = $currentTranscription.result.text;
		}
	}

	const copyToClipboard = () => {
		navigator.clipboard.writeText(transcriptionText).then(
			() => {
				toast.success('Text copied to clipboard!');
			},
			() => {
				toast.error('Failed to copy text.');
			}
		);
	};

	// Download handlers (simplified reusing existing utils or custom logic)
	const downloadFile = (format) => {
		const id = $currentTranscription.id;
		window.location.href = `${CLIENT_API_HOST}/api/download/${id}?format=${format}`;
	};

	let wordCount = 0;
	$: if (
		$currentTranscription &&
		$currentTranscription.result &&
		$currentTranscription.result.text
	) {
		wordCount = $currentTranscription.result.text.split(/\s+/).filter((w) => w.length > 0).length;
	}
</script>

<Toaster />

{#if $currentTranscription}
	<div class="min-h-screen bg-base-100 p-4 md:p-8" in:fade>
		<!-- Header / Nav -->
		<div
			class="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between"
		>
			<div class="flex items-center gap-4">
				<a href="/" class="btn btn-circle btn-ghost btn-sm opacity-60 hover:opacity-100">
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
							d="M10 19l-7-7m0 0l7-7m-7 7h18"
						/></svg
					>
				</a>
				<div>
					<h1 class="text-2xl md:text-3xl font-bold tracking-tight text-base-content">
						{$currentTranscription.fileName.split('_WHSHPR_')[1]}
					</h1>
					<div class="flex items-center gap-2 mt-1 text-sm opacity-60">
						<span class="font-mono text-xs uppercase bg-base-200 px-1.5 py-0.5 rounded"
							>{$currentTranscription.id}</span
						>
						<span>•</span>
						<span>{formatDate($currentTranscription.id)}</span>
					</div>
				</div>
			</div>

			<div class="flex items-center gap-2">
				<a
					href="/editor/{$currentTranscription.id}"
					class="btn btn-primary gap-2 shadow-lg shadow-primary/20"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-4 h-4"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path
							d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
						></path></svg
					>
					Open Editor
				</a>
			</div>
		</div>

		<div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
			<!-- Left Column: Details & Stats -->
			<div class="space-y-6">
				<!-- Info Card -->
				<div class="card bg-base-200/50 border border-base-content/5 shadow-sm">
					<div class="card-body p-6">
						<h3 class="card-title text-base uppercase font-bold opacity-60 mb-4">Details</h3>

						<div class="space-y-4">
							<div class="flex justify-between items-center pb-3 border-b border-base-content/5">
								<span class="flex items-center gap-2 opacity-80">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="w-4 h-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
										><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"
										></polyline></svg
									>
									Duration
								</span>
								<span class="font-mono font-bold"
									>{formatTime($currentTranscription.result.duration)}</span
								>
							</div>
							<div class="flex justify-between items-center pb-3 border-b border-base-content/5">
								<span class="flex items-center gap-2 opacity-80">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="w-4 h-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
										><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path
											d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"
										></path></svg
									>
									Word Count
								</span>
								<span class="font-mono font-bold">{wordCount}</span>
							</div>
							<div class="flex justify-between items-center pb-3 border-b border-base-content/5">
								<span class="flex items-center gap-2 opacity-80">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="w-4 h-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
										><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"
										></line><path
											d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"
										></path></svg
									>
									Language
								</span>
								<span class="badge badge-neutral font-bold uppercase"
									>{$currentTranscription.result.language}</span
								>
							</div>
							<div class="flex justify-between items-center pb-3 border-b border-base-content/5">
								<span class="flex items-center gap-2 opacity-80">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="w-4 h-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
										><path
											d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"
										></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line
											x1="12"
											y1="22.08"
											x2="12"
											y2="12"
										></line></svg
									>
									Model
								</span>
								<span class="badge badge-outline font-mono text-xs"
									>{$currentTranscription.modelSize}</span
								>
							</div>
						</div>
					</div>
				</div>

				<!-- Downloads Card -->
				<div class="card bg-base-200/50 border border-base-content/5 shadow-sm">
					<div class="card-body p-6">
						<h3 class="card-title text-base uppercase font-bold opacity-60 mb-4">Download</h3>
						<div class="grid grid-cols-2 gap-3">
							<button class="btn btn-outline btn-sm" on:click={() => downloadFile('srt')}
								>SRT</button
							>
							<button class="btn btn-outline btn-sm" on:click={() => downloadFile('vtt')}
								>VTT</button
							>
							<button class="btn btn-outline btn-sm" on:click={() => downloadFile('txt')}
								>TXT</button
							>
							<button class="btn btn-outline btn-sm" on:click={() => downloadFile('json')}
								>JSON</button
							>
						</div>
					</div>
				</div>
			</div>

			<!-- Right Column: Transcript View -->
			<div class="lg:col-span-2">
				<div class="card bg-base-100 border border-base-content/10 shadow-lg h-[calc(100vh-12rem)]">
					<!-- Toolbar -->
					<div
						class="p-4 border-b border-base-content/10 flex justify-between items-center bg-base-200/30 rounded-t-2xl"
					>
						<div class="flex items-center gap-4">
							<h3 class="font-bold text-lg">Transcript</h3>
							<label class="label cursor-pointer gap-2 hover:opacity-100 transition-opacity">
								<span class="label-text text-xs uppercase font-bold opacity-60"
									>Show Timestamps</span
								>
								<input
									type="checkbox"
									class="toggle toggle-primary toggle-sm"
									bind:checked={showTimestamps}
								/>
							</label>
						</div>

						<button class="btn btn-sm btn-ghost gap-2" on:click={copyToClipboard}>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="w-4 h-4"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path
									d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
								></path></svg
							>
							Copy
						</button>
					</div>

					<!-- Content -->
					<div class="flex-1 overflow-y-auto p-6 md:p-8 bg-base-100 rounded-b-2xl">
						<pre
							class="whitespace-pre-wrap font-sans text-base leading-loose text-base-content/90 max-w-none">{transcriptionText}</pre>
					</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="flex items-center justify-center min-h-screen">
		<span class="loading loading-spinner loading-lg"></span>
	</div>
{/if}
