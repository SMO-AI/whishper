<script>
	import { validateURL, CLIENT_API_HOST } from '$lib/utils.js';
	import { env } from '$env/dynamic/public';
	import { uploadProgress } from '$lib/stores';
	import { supabase } from '$lib/supabase'; // Import Supabase

	import toast from 'svelte-french-toast';

	let errorMessage = '';
	let disableSubmit = true;
	let modelSize = 'groq:whisper-large-v3'; // Default to Groq V3 as requested
	let language = 'auto';
	let sourceUrl = '';
	let fileInput;
	let device = env.PUBLIC_WHISHPER_PROFILE == 'gpu' ? 'cuda' : 'cpu';
	let task = 'transcribe';
	let activeTab = 'file'; // 'file' or 'url';

	let languages = [
		{ value: 'auto', label: 'Auto Detect' },
		{ value: 'ru', label: 'Russian' },
		{ value: 'en', label: 'English' },
		{ value: 'es', label: 'Spanish' },
		{ value: 'fr', label: 'French' }
	];
	// Models defined below
	let models = [
		{ value: 'medium', label: 'Whisper Medium' },
		{ value: 'groq:distil-whisper-large-v3-en', label: 'Groq Distil Whisper Large V3 (EN)' },
		{ value: 'groq:whisper-large-v3', label: 'Groq Whisper Large V3' },
		{ value: 'groq:whisper-large-v3-turbo', label: 'Groq Whisper Large V3 Turbo' }
	];

	// Function that sends the data as a form to the backend
	async function sendForm() {
		if (sourceUrl && !validateURL(sourceUrl)) {
			toast.error('You must enter a valid URL.');
			return;
		}

		if (!sourceUrl && (!fileInput || !fileInput.files || fileInput.files.length === 0)) {
			toast.error('No file or URL.');
			return;
		}

		let formData = new FormData();
		formData.append('language', language);
		formData.append('modelSize', modelSize);
		formData.append('task', task);
		if (device == 'cuda' || device == 'cpu') {
			formData.append('device', device);
		} else {
			formData.append('device', 'cpu');
		}
		formData.append('sourceUrl', sourceUrl);
		if (sourceUrl == '' && fileInput && fileInput.files.length > 0) {
			formData.append('file', fileInput.files[0]);
		}

		// Get Session
		const {
			data: { session }
		} = await supabase.auth.getSession();
		const accessToken = session?.access_token;

		return new Promise((resolve, reject) => {
			const xhr = new XMLHttpRequest();

			// Set up progress event listener
			xhr.upload.addEventListener('progress', (event) => {
				if (event.lengthComputable) {
					const percentCompleted = Math.round((event.loaded * 100) / event.total);
					uploadProgress.set(percentCompleted);
				}
			});

			// Set up load event listener
			xhr.addEventListener('load', () => {
				if (xhr.status === 200) {
					resolve(xhr.response);
					toast.success('Success!');
					// Close the modal programmatically
					document.getElementById('modalNewTranscription').close();
				} else {
					reject(xhr.statusText);
					toast.error('Upload failed');
				}
				uploadProgress.set(0); // Reset progress after completion
			});

			// Set up error event listener
			xhr.addEventListener('error', () => {
				reject(xhr.statusText);
				toast.error('An error occurred during upload');
				uploadProgress.set(0); // Reset progress on error
			});

			xhr.open('POST', `${CLIENT_API_HOST}/api/transcriptions`);
			if (accessToken) {
				xhr.setRequestHeader('Authorization', `Bearer ${accessToken}`);
			}
			xhr.send(formData);
		});

		// Set file and sourceUrl to empty
		sourceUrl = '';
		if (fileInput) fileInput.value = '';
		uploadProgress.set(0);

		toast.success('Success!');
	}

	// Reactive statement
	$: if (sourceUrl && !validateURL(sourceUrl)) {
		errorMessage = 'Enter a valid URL';
		disableSubmit = true;
	} else {
		errorMessage = '';
		// Check invalid state more thoroughly
		if (activeTab === 'url' && (!sourceUrl || !validateURL(sourceUrl))) {
			disableSubmit = true;
		} else if (
			activeTab === 'file' &&
			(!fileInput || !fileInput.files || fileInput.files.length === 0)
		) {
			// We can't really reactively track file input changes easily without binding event
			// But valid URL logic handles the URL part.
			// For file input, we usually rely on the user picking something.
			// Let's assume false if no error for now, but button click will validate.
			disableSubmit = false;
		} else {
			disableSubmit = false;
		}
	}

	// Tiny helper to handle file selection to update UI state if needed
	let fileName = '';
	const handleFileChange = (e) => {
		if (e.target.files.length > 0) {
			fileName = e.target.files[0].name;
			disableSubmit = false;
		} else {
			fileName = '';
			disableSubmit = true;
		}
	};
</script>

<dialog id="modalNewTranscription" class="modal">
	<form
		method="dialog"
		class="modal-box w-11/12 max-w-2xl bg-base-100 p-0 overflow-hidden rounded-3xl shadow-2xl"
	>
		<!-- Header -->
		<div
			class="bg-base-200/50 p-6 border-b border-base-content/5 flex justify-between items-center"
		>
			<div>
				<h3 class="font-bold text-2xl">New Transcription</h3>
				<p class="text-sm opacity-60">Upload audio or video to transcribe</p>
			</div>
			<button class="btn btn-circle btn-ghost btn-sm">✕</button>
		</div>

		<div class="p-6 md:p-8 space-y-6">
			<!-- Tabs -->
			<div role="tablist" class="tabs tabs-boxed bg-base-200/50 p-1 rounded-xl">
				<button
					type="button"
					role="tab"
					class="tab transition-all duration-300 rounded-lg {activeTab === 'file'
						? 'tab-active bg-primary text-primary-content shadow-md'
						: ''}"
					on:click={() => {
						activeTab = 'file';
						sourceUrl = '';
					}}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-4 h-4 mr-2"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
						/></svg
					>
					Upload File
				</button>
				<button
					type="button"
					role="tab"
					class="tab transition-all duration-300 rounded-lg {activeTab === 'url'
						? 'tab-active bg-primary text-primary-content shadow-md'
						: ''}"
					on:click={() => {
						activeTab = 'url';
						if (fileInput) fileInput.value = '';
						fileName = '';
					}}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-4 h-4 mr-2"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
						/></svg
					>
					Import from URL
				</button>
			</div>

			<!-- Content Area -->
			<div class="min-h-[160px] flex flex-col justify-center">
				{#if activeTab === 'file'}
					<div class="w-full">
						<label
							class="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-2xl cursor-pointer bg-base-200/30 border-base-content/20 hover:bg-base-200 hover:border-primary/50 transition-all group relative overflow-hidden"
						>
							<div class="flex flex-col items-center justify-center pt-5 pb-6 z-10">
								{#if fileName}
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="w-10 h-10 text-success mb-3"
										fill="none"
										viewBox="0 0 24 24"
										stroke="currentColor"
										><path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
										/></svg
									>
									<p class="mb-2 text-sm text-base-content font-semibold">{fileName}</p>
									<p class="text-xs text-base-content/60">Click to change file</p>
								{:else}
									<svg
										aria-hidden="true"
										class="w-10 h-10 mb-3 text-base-content/40 group-hover:text-primary transition-colors"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
										xmlns="http://www.w3.org/2000/svg"
										><path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
										/></svg
									>
									<p class="mb-2 text-sm text-base-content/70">
										<span class="font-semibold">Click to upload</span> or drag and drop
									</p>
									<p class="text-xs text-base-content/50">MP3, MP4, WAV, M4A (MAX. 150MB)</p>
								{/if}
							</div>
							<!-- Background accent -->
							<div
								class="absolute inset-0 bg-primary/5 scale-0 group-hover:scale-100 rounded-2xl transition-transform duration-500 origin-center"
							/>

							<input
								name="file"
								bind:this={fileInput}
								type="file"
								class="hidden"
								on:change={handleFileChange}
							/>
						</label>
					</div>
				{:else}
					<div class="form-control w-full">
						<label class="label">
							<span class="label-text font-bold">Paste URL</span>
						</label>
						<div class="relative">
							<input
								name="sourceUrl"
								bind:value={sourceUrl}
								type="text"
								placeholder="https://youtube.com/watch?v=..."
								class="input input-lg input-bordered w-full pl-12 focus:input-primary transition-all"
							/>
							<div
								class="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-base-content/40"
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
										d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
									/></svg
								>
							</div>
						</div>
						<label class="label">
							{#if errorMessage}
								<span class="label-text-alt text-error">{errorMessage}</span>
							{:else}
								<span class="label-text-alt opacity-50"
									>Supported: YouTube, generic video/audio URLs</span
								>
							{/if}
						</label>
					</div>
				{/if}
			</div>

			<!-- Configuration Grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-base-content/10">
				<div class="form-control w-full">
					<label class="label">
						<span class="label-text font-bold text-sm">Model</span>
					</label>
					<select name="modelSize" bind:value={modelSize} class="select select-bordered w-full">
						{#each models as m}
							<option value={m.value}>{m.label}</option>
						{/each}
					</select>
				</div>

				<div class="form-control w-full">
					<label class="label">
						<span class="label-text font-bold text-sm">Language</span>
					</label>
					<select name="language" bind:value={language} class="select select-bordered w-full">
						{#each languages as l}
							<option value={l.value}>{l.label}</option>
						{/each}
					</select>
				</div>
			</div>
		</div>

		<!-- Footer Actions -->
		<div
			class="modal-action bg-base-200/50 p-6 m-0 border-t border-base-content/5 flex justify-end gap-3"
		>
			<!-- Hidden inputs for device and task to be safe, though variables are bound -->
			<input type="hidden" name="device" value={device} />
			<input type="hidden" name="task" value={task} />

			<form method="dialog">
				<button class="btn btn-ghost hover:bg-base-300">Cancel</button>
			</form>
			<button
				class="btn btn-primary px-8 shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all font-bold tracking-wide"
				on:click={sendForm}
				disabled={disableSubmit}
			>
				{#if disableSubmit}
					Fill required fields
				{:else}
					Start Transcription
				{/if}
			</button>
		</div>
	</form>
	<form method="dialog" class="modal-backdrop bg-base-300/80 backdrop-blur-sm">
		<button>close</button>
	</form>
</dialog>
