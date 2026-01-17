<script>
	import { onMount, onDestroy } from 'svelte';
	import { writable } from 'svelte/store';
	import toast from 'svelte-french-toast';
	import { editorSettings, currentTranscription, editorHistory, t } from '$lib/stores';

	import EditorSettings from './EditorSettings.svelte';
	import EditorSegment from './EditorSegment.svelte';
	import { CLIENT_API_HOST } from '$lib/utils';

	let language = writable('original');

	// AI Error Checking
	let checkingErrors = false;
	let errors = {}; // Map: segmentId -> correctedText

	async function checkErrors() {
		if (checkingErrors) return;
		checkingErrors = true;
		errors = {};

		const loadingId = toast.loading('AI is checking for errors...');

		try {
			// Select segments based on current language
			const segments =
				$language == 'original'
					? $currentTranscription.result.segments
					: $currentTranscription.translations.find((t) => t.targetLanguage == $language).result
							.segments;

			const res = await fetch('/ai/check', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ segments })
			});

			const data = await res.json();

			if (data.error) throw new Error(data.error);

			errors = data.corrections || {};

			if (Object.keys(errors).length === 0) {
				toast.success('No errors found!', { id: loadingId });
			} else {
				toast.error(`Found ${Object.keys(errors).length} segments with errors.`, { id: loadingId });
			}
		} catch (e) {
			console.error(e);
			toast.error('Failed to check errors: ' + e.message, { id: loadingId });
		} finally {
			checkingErrors = false;
		}
	}

	function fixError(id) {
		const newErrors = { ...errors };
		delete newErrors[id];
		errors = newErrors;
	}

	function fixAllErrors() {
		// Apply all fixes
		const source =
			$language == 'original'
				? $currentTranscription.result.segments
				: $currentTranscription.translations.find((t) => t.targetLanguage == $language).result
						.segments;

		let updated = false;
		source.forEach((seg) => {
			if (errors[seg.id]) {
				seg.text = errors[seg.id];
				updated = true;
			}
		});

		if (updated) {
			$currentTranscription = { ...$currentTranscription };
			errors = {};
			toast.success('All errors fixed!');

			// Update history
			let currentT = JSON.parse(JSON.stringify($currentTranscription));
			editorHistory.update((value) => {
				return [...value, currentT];
			});
		}
	}

	// Segments lazy loading
	let segmentsToShow = 20;
	function loadMore() {
		segmentsToShow += 10;
	}
	let loadMoreButton;

	async function textFromSegments() {
		let text = '';
		if ($language == 'original') {
			text = $currentTranscription.result.segments
				.map((segment) => segment.text)
				.join(' ')
				.replace(/(\r\n|\n|\r)/gm, ' ');
		} else {
			text = $currentTranscription.translations
				.filter((translation) => translation.targetLanguage == $language)[0]
				.result.segments.map((segment) => segment.text)
				.join(' ')
				.replace(/(\r\n|\n|\r)/gm, ' ');
		}
		console.log(text);
		return text;
	}

	async function saveChanges() {
		var url = `${CLIENT_API_HOST}/api/transcriptions`; // replace with your actual endpoint
		console.log($language);
		// Update text to match segments
		if ($language == 'original') {
			$currentTranscription.result.text = await textFromSegments();
		} else {
			$currentTranscription.translations.forEach(async (translation) => {
				if (translation.targetLanguage == $language)
					translation.result.text = await textFromSegments();
			});
		}

		try {
			const response = await fetch(url, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify($currentTranscription)
			});

			if (!response.ok) {
				if (response.status === 304) {
					if (!$editorSettings.autoSave) {
						toast('No changes were made!', {
							icon: '👐'
						});
					}
					return;
				} else {
					toast.error("Couldn't save!");
					throw new Error(`HTTP error! status: ${response.status}`);
				}
			}

			if ($editorSettings.autoSave) {
				toast('Autosaving...', { icon: 'ℹ️' });
			} else {
				toast.success('Saved!');
			}
		} catch (error) {
			toast.error("Couldn't save!");
			console.error('Error:', error);
		}
	}

	let handleKeyDown;
	let observer;
	onMount(() => {
		// Lazy loading
		observer = new IntersectionObserver((entries) => {
			entries.forEach((entry) => {
				if (entry.isIntersecting) {
					loadMore();
				}
			});
		});
		observer.observe(loadMoreButton);

		// Function to handle Ctrl+Z and Ctrl+S shortcuts
		editorHistory.set([JSON.parse(JSON.stringify($currentTranscription))]);
		let isUndoing = false;
		handleKeyDown = function (e) {
			// Undo (CTRL+Z)
			if (e.ctrlKey && e.key === 'z' && !isUndoing) {
				isUndoing = true;
				let previousTranscription = null;

				editorHistory.update((history) => {
					if (history.length > 1) {
						history = history.slice(0, -1);
						previousTranscription = { ...history[history.length - 1] };
					}
					return history;
				});

				if (previousTranscription) {
					$currentTranscription = { ...previousTranscription };
				}
				isUndoing = false;
			}

			let isSaving = false;
			if (e.ctrlKey && e.key === 's') {
				e.preventDefault();
				if (!isSaving) {
					isSaving = true;
					saveChanges();
					isSaving = false;
				}
			}
		};

		if (!$editorSettings.autoSave) {
			toast('Autosave is disabled.', {
				icon: '👋'
			});
		}

		// Listen to keydown event
		document.addEventListener('keydown', handleKeyDown);
	});

	// Autosave
	let autosaveInterval;
	let autoSaveAux = $editorSettings.autoSave;
	$: if ($editorSettings.autoSave) {
		toast.success('Autosave enabled.');
		autoSaveAux = true;
		autosaveInterval = setInterval(() => {
			saveChanges();
		}, $editorSettings.autosaveInterval);
	} else {
		if (autoSaveAux == true) {
			toast('Autosave is disabled.', {
				icon: '👋'
			});
			autoSaveAux = false;
		}
		clearInterval(autosaveInterval);
	}
</script>

{#if $currentTranscription.status != 2}
	<div class="flex items-center justify-center">
		<span class="loading loading-spinner loading-lg" />
		<p class="text-center">
			Waiting for task to finish {$currentTranscription.status == 3
				? 'translating'
				: 'transcribing'}...
		</p>
	</div>
{:else}
	<div class="flex flex-col h-full relative bg-base-100">
		<!-- Sticky Header -->
		<div
			class="sticky top-0 z-30 bg-base-100/95 backdrop-blur-md border-b border-base-content/10 px-4 py-3 md:px-6 md:py-4 shadow-sm transition-all"
		>
			<div class="flex flex-col gap-4">
				<!-- Top Row: Title & Main Actions -->
				<div class="flex items-center justify-between gap-4">
					<div class="flex-1 min-w-0 flex items-center gap-3">
						<a
							href="/app"
							class="btn btn-ghost btn-sm btn-circle opacity-60 hover:opacity-100 transition-opacity"
							title="Back to Home"
						>
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

						<div class="flex flex-col overflow-hidden">
							<h1
								class="text-lg md:text-xl font-bold truncate leading-tight tracking-tight"
								title={$currentTranscription.fileName}
							>
								{$currentTranscription.fileName.split('_WHSHPR_')[1]}
							</h1>
							<span class="text-[10px] uppercase font-bold tracking-widest opacity-40"
								>Editor Mode</span
							>
						</div>
					</div>

					<div class="flex items-center gap-2">
						<button
							on:click={saveChanges}
							class="btn btn-primary btn-sm gap-2 shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all font-bold"
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
								><path
									d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"
								/><polyline points="17 21 17 13 7 13 7 21" /><polyline points="7 3 7 8 15 8" /></svg
							>
							<span class="hidden md:inline">Save Changes</span>
						</button>
					</div>
				</div>

				<!-- Bottom Row: Settings & Filters -->
				<div class="flex flex-wrap items-center justify-between gap-4 pt-1 pl-12 pr-1">
					<EditorSettings />

					<!-- AI Actions -->
					<div class="flex items-center gap-2">
						{#if Object.keys(errors).length > 0}
							<button
								on:click={fixAllErrors}
								class="btn btn-xs btn-success gap-1 text-white shadow-sm hover:shadow-md transition-all"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="w-3 h-3"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg
								>
								Fix All Errors ({Object.keys(errors).length})
							</button>
						{/if}
						<button
							on:click={checkErrors}
							class="btn btn-xs btn-ghost gap-1 border border-base-content/20 hover:border-primary hover:text-primary transition-all ml-2"
							disabled={checkingErrors}
						>
							{#if checkingErrors}
								<span class="loading loading-spinner loading-xs" />
							{:else}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="w-3 h-3"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
									><path
										d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 0 1 9-9"
									/></svg
								>
							{/if}
							AI Check
						</button>
					</div>

					{#if $currentTranscription.translations.length > 0}
						<select
							bind:value={$language}
							name="language"
							class="select select-xs select-bordered max-w-xs font-mono uppercase bg-base-200/50 focus:bg-base-100 transition-all"
						>
							<option value="original"
								>✅ {$t('original')} ({$currentTranscription.result.language})</option
							>
							{#each $currentTranscription.translations as translation, translationIndex}
								<option value={translation.targetLanguage}>🤖 {translation.targetLanguage}</option>
							{/each}
						</select>
					{/if}
				</div>
			</div>
		</div>

		<!-- Scrollable Content -->
		<div class="flex-1 overflow-y-auto custom-scrollbar bg-base-200/30 p-2 md:p-6">
			<div class="max-w-6xl mx-auto">
				<table class="table table-pin-rows w-full border-separate border-spacing-y-3">
					<thead>
						<tr class="text-base-content/40 text-[10px] uppercase font-bold tracking-wider">
							<th class="bg-transparent pl-4 border-b-0 hidden md:table-cell">#</th>
							<th class="bg-transparent border-b-0">{$t('timing')}</th>
							<th class="bg-transparent w-full border-b-0">{$t('transcribe')}</th>
							<th class="bg-transparent border-b-0 hidden md:table-cell">{$t('metrics')}</th>
							<th class="bg-transparent pr-4 text-right border-b-0">{$t('actions')}</th>
						</tr>
					</thead>
					<tbody class="text-sm">
						{#if $language == 'original'}
							{#each $currentTranscription.result.segments.slice(0, segmentsToShow) as segment, index (segment.id)}
								<EditorSegment
									{segment}
									{index}
									translationIndex={-1}
									error={errors[segment.id]}
									on:fix={() => fixError(segment.id)}
								/>
							{/each}
						{:else}
							{#each $currentTranscription.translations as translation, translationIndex}
								{#if translation.targetLanguage == $language}
									{#each translation.result.segments.slice(0, segmentsToShow) as segment, index (segment.id)}
										<EditorSegment
											{segment}
											{index}
											{translationIndex}
											error={errors[segment.id]}
											on:fix={() => fixError(segment.id)}
										/>
									{/each}
								{/if}
							{/each}
						{/if}
					</tbody>
				</table>

				<!-- Load More / Trigger -->
				<div class="py-12 flex justify-center w-full">
					<button
						bind:this={loadMoreButton}
						class="btn btn-ghost btn-sm opacity-30 hover:opacity-100 transition-opacity"
					>
						{#if $language == 'original'}
							{#if segmentsToShow >= $currentTranscription.result.segments.length}
								<span class="text-xs italic">{$t('end_transcription')}</span>
							{:else}
								<span class="loading loading-dots loading-xs" />
							{/if}
						{:else if segmentsToShow >= $currentTranscription.translations.filter((translation) => translation.targetLanguage == $language)[0].result.segments.length}
							<span class="text-xs italic">{$t('end_transcription')}</span>
						{:else}
							<span class="loading loading-dots loading-xs" />
						{/if}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
