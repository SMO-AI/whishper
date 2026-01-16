<script>
	import { downloadSRT, downloadTXT, downloadJSON, downloadVTT, CLIENT_API_HOST } from '$lib/utils';
	import { supabase } from '$lib/supabase';
	import toast from 'svelte-french-toast';
	export let tr;

	let subtitleFormat = 'srt';
	let language = 'original';

	function downloadSubtitle() {
		console.log('download subtitle');
		let segments = [];
		let text = '';
		let title = 'subtitles';

		console.log(language);
		if (language == 'original') {
			segments = tr.result.segments;
			text = tr.result.text;
			title = tr.fileName.split('_WHSHPR_')[1];
		} else {
			for (const translation of tr.translations) {
				if (translation.targetLanguage == language) {
					segments = translation.result.segments;
					text = translation.result.text;
					title = tr.fileName.split('_WHSHPR_')[1];
					break;
				}
			}
		}

		if (segments.length == 0 || text == '') {
			toast.error('No data available for download');
			return;
		}

		if (subtitleFormat == 'srt') {
			downloadSRT(segments, title);
		} else if (subtitleFormat == 'vtt') {
			downloadVTT(segments, title);
		} else if (subtitleFormat == 'json') {
			downloadJSON(tr.result, title);
		} else if (subtitleFormat == 'txt') {
			downloadTXT(text, title);
		}
	}

	async function downloadMedia() {
		const {
			data: { session }
		} = await supabase.auth.getSession();
		const accessToken = session?.access_token;
		if (!accessToken) {
			toast.error('Authentication required');
			return;
		}

		try {
			const response = await fetch(`${CLIENT_API_HOST}/api/video/${tr.fileName}`, {
				headers: {
					Authorization: `Bearer ${accessToken}`
				}
			});

			if (!response.ok) {
				throw new Error('Download failed');
			}

			const blob = await response.blob();
			const url = window.URL.createObjectURL(blob);
			const link = document.createElement('a');
			link.href = url;
			link.download = tr.fileName.split('_WHSHPR_')[1] || tr.fileName;
			document.body.appendChild(link);
			link.click();
			link.remove();
			window.URL.revokeObjectURL(url);
		} catch (error) {
			console.error(error);
			toast.error($t('error_media_download_failed'));
		}
	}

	async function copyText() {
		console.log('copy text');
		let text = '';
		if (language == 'original') {
			text = tr.result.text;
		} else {
			for (const translation of tr.translations) {
				console.log(translation.targetLanguage == language);
				if (translation.targetLanguage == language) {
					text = translation.result.text;
					break;
				}
			}
		}
		// Copy tr.result.text to clipboard
		try {
			await navigator.clipboard.writeText(text);
			console.log('Text copied to clipboard');
			toast.success($t('success_copy'));
		} catch (err) {
			console.error('Error in copying text: ', err);
		}
	}
</script>

<dialog id="modalDownloadOptions" class="modal">
	<form method="dialog" class="modal-box flex flex-col items-center justify-center">
		<button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
		{#if tr}
			<h1 class="text-center font-bold mt-2 pb-2">{$t('download_options')}</h1>

			<div class="flex flex-row space-x-4">
				<div class="form-control">
					<label for="format" class="label">
						<span class="label-text font-bold">{$t('file_format')}</span>
					</label>
					<select
						bind:value={subtitleFormat}
						name="format"
						class="select select-bordered w-full max-w-xs"
					>
						<option value="srt">SRT</option>
						<option value="vtt">VTT</option>
						<option value="json">JSON</option>
						<option value="txt">TXT</option>
					</select>
				</div>

				<div class="form-control">
					<label for="language" class="label">
						<span class="label-text font-bold">{$t('text_language')}</span>
					</label>
					<select
						bind:value={language}
						name="language"
						class="select select-bordered w-full max-w-xs uppercase"
					>
						<option value="original">✅ {$t('original')} ({tr.result.language})</option>
						{#each tr.translations as translation}
							<option value={translation.targetLanguage}>🤖 {translation.targetLanguage}</option>
						{/each}
					</select>
				</div>
			</div>

			<div class="space-x-2 mt-8">
				<span class="tooltip" data-tip="Download {subtitleFormat} file in {language}.">
					<button on:click={downloadSubtitle} class="btn btn-sm btn-success">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="icon icon-tabler icon-tabler-download"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							stroke-width="2"
							stroke="currentColor"
							fill="none"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path stroke="none" d="M0 0h24v24H0z" fill="none" />
							<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2" />
							<path d="M7 11l5 5l5 -5" />
							<path d="M12 4l0 12" />
						</svg>
						<span> File </span>
					</button>
				</span>
				<span class="tooltip" data-tip="Copy raw text in '{language}' language.">
					<button on:click={copyText} class="btn btn-sm btn-info">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="icon icon-tabler icon-tabler-copy"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							stroke-width="2"
							stroke="currentColor"
							fill="none"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path stroke="none" d="M0 0h24v24H0z" fill="none" />
							<path
								d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z"
							/>
							<path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2" />
						</svg>
						<span> Copy </span>
					</button>
				</span>
				<span class="tooltip" data-tip="Download source media">
					<button on:click={downloadMedia} class="btn btn-sm btn-error">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="icon icon-tabler icon-tabler-file-download"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							stroke-width="2"
							stroke="currentColor"
							fill="none"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path stroke="none" d="M0 0h24v24H0z" fill="none" />
							<path d="M14 3v4a1 1 0 0 0 1 1h4" />
							<path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
							<path d="M12 17v-6" />
							<path d="M9.5 14.5l2.5 2.5l2.5 -2.5" />
						</svg>
						<span> Media </span>
					</button>
				</span>
			</div>
		{:else}
			<div class="flex items-center justify-center w-screen h-screen">
				<h1>
					<span class="loading loading-bars loading-lg" />
				</h1>
			</div>
		{/if}
	</form>
	<form method="dialog" class="modal-backdrop">
		<button>close</button>
	</form>
</dialog>
