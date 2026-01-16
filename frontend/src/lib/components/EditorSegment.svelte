<script>
	import { editorSettings } from '$lib/stores';
	import { currentVideoPlayerTime, currentTranscription, editorHistory } from '$lib/stores';
	export let index;
	export let segment;
	export let translationIndex;

	let isActive = false;

	function getCps(s) {
		// Find duration
		let duration = s.end - s.start;

		// Count characters
		let charCount = s.text.length;

		// Calculate CPS
		let cps = charCount / duration;

		// Round to 2 decimals
		cps = Math.round(cps * 100) / 100;
		// Truncate to integer
		return Math.trunc(cps);
	}

	function deleteSegment(index, callback) {
		console.log($currentTranscription);
		const source =
			translationIndex == -1
				? $currentTranscription.result.segments
				: $currentTranscription.translations[translationIndex].result.segments;
		source.splice(index, 1);
		// Update index
		$currentTranscription = { ...$currentTranscription }; // deep copy
		callback();
	}

	// This function takes a segment and splits it into two segments at the given index
	function splitSegment(index, callback) {
		// Choose the correct source based on translationIndex
		const source =
			translationIndex == -1
				? $currentTranscription.result.segments
				: $currentTranscription.translations[translationIndex].result.segments;

		const segment = source[index];
		const words = segment.text.split(' ');
		const half = Math.ceil(words.length / 2);
		const firstHalf = words.slice(0, half).join(' ');
		const secondHalf = words.slice(half).join(' ');

		const duration = segment.end - segment.start;
		const midTime = segment.start + duration / 2;

		// Update current segment
		segment.text = firstHalf;
		segment.end = midTime;

		// Create and insert new segment
		const newSegment = {
			id: JSON.stringify(Date.now()),
			start: midTime,
			end: segment.end + duration / 2,
			text: secondHalf,
			words: []
		};
		source.splice(index + 1, 0, newSegment);

		$currentTranscription = { ...$currentTranscription };
		callback();
	}

	// Text changes only save after 6 keystrokes
	let keystrokes = 0;
	function handleKeystrokes() {
		keystrokes++;
		if (keystrokes > 6) {
			handleHistory();
			keystrokes = 0;
		}
	}

	// Save history on editing
	function handleHistory() {
		let currentT = JSON.parse(JSON.stringify($currentTranscription));
		editorHistory.update((value) => {
			return [...value, currentT];
		});
	}

	function insertSegmentAbove(index, callback) {
		const source =
			translationIndex == -1
				? $currentTranscription.result.segments
				: $currentTranscription.translations[translationIndex].result.segments;
		source.splice(index, 0, {
			id: JSON.stringify(Date.now()),
			start: 0,
			end: 0,
			text: '',
			words: []
		});
		$currentTranscription = { ...$currentTranscription }; // deep copy
		callback();
	}

	function insertSegmentBelow(index, callback) {
		const source =
			translationIndex == -1
				? $currentTranscription.result.segments
				: $currentTranscription.translations[translationIndex].result.segments;
		source.splice(index + 1, 0, {
			id: JSON.stringify(Date.now()),
			start: 0,
			end: 0,
			text: '',
			words: []
		});
		$currentTranscription = { ...$currentTranscription }; // deep copy
		callback();
	}

	$: if (segment.start <= $currentVideoPlayerTime && $currentVideoPlayerTime <= segment.end) {
		isActive = true;
	} else {
		isActive = false;
	}
</script>

<tr
	class="group text-sm transition-all duration-300 relative {isActive
		? 'scale-[1.01]'
		: 'hover:scale-[1.005]'}"
>
	<!-- ID Column -->
	<td
		class="bg-base-100 rounded-l-2xl border-l-[3px] shadow-sm align-top py-4 {isActive
			? 'border-primary shadow-md'
			: 'border-base-content/5 group-hover:border-primary/50'}"
	>
		<div class="font-mono text-xs opacity-40 font-bold ml-2">#{index + 1}</div>
	</td>

	<!-- Timing Column -->
	<td class="bg-base-100 shadow-sm align-top py-4 min-w-[140px] {isActive ? 'shadow-md' : ''}">
		<div class="flex flex-col gap-2">
			<!-- Start input -->
			<div class="relative group/time">
				<input
					class="w-full input input-xs input-ghost font-mono text-xs bg-base-200/50 focus:bg-base-100 focus:input-primary text-center tracking-wider"
					type="number"
					step="0.01"
					bind:value={segment.start}
					on:input={(e) => $currentVideoPlayerTime.set(e.target.value)}
					on:input={handleHistory}
					on:click={(e) => {
						if ($editorSettings.seekOnClick) $currentVideoPlayerTime = e.target.value;
					}}
				/>
				<button
					on:click={() => {
						segment.start = $currentVideoPlayerTime;
						handleHistory();
					}}
					class="absolute -right-6 top-0 btn btn-xs btn-circle btn-ghost opacity-0 group-hover/time:opacity-100 text-primary tooltip tooltip-right z-10"
					data-tip="Set start to current time"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-3 h-3"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/></svg
					>
				</button>
			</div>

			<!-- End input -->
			<div class="relative group/time">
				<input
					class="w-full input input-xs input-ghost font-mono text-xs bg-base-200/50 focus:bg-base-100 focus:input-primary text-center tracking-wider"
					type="number"
					step="0.01"
					bind:value={segment.end}
					on:input={(e) => ($currentVideoPlayerTime = e.target.value)}
					on:input={handleHistory}
					on:click={(e) => {
						if ($editorSettings.seekOnClick) $currentVideoPlayerTime = e.target.value;
					}}
				/>
				<button
					on:click={() => {
						segment.end = $currentVideoPlayerTime;
						handleHistory();
					}}
					class="absolute -right-6 top-0 btn btn-xs btn-circle btn-ghost opacity-0 group-hover/time:opacity-100 text-primary tooltip tooltip-right z-10"
					data-tip="Set end to current time"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-3 h-3"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/></svg
					>
				</button>
			</div>

			{#if isActive}
				<div class="badge badge-primary badge-xs font-bold mx-auto mt-1 animate-pulse">ACTIVE</div>
			{/if}
		</div>
	</td>

	<!-- Text Column -->
	<td class="bg-base-100 shadow-sm align-top py-4 {isActive ? 'shadow-md' : ''}">
		<!-- Text input -->
		<div
			bind:textContent={segment.text}
			on:input={handleKeystrokes}
			class="w-full p-3 font-sans text-base leading-relaxed border border-transparent rounded-lg hover:border-base-content/10 focus:border-primary focus:bg-base-50 outline-none transition-all placeholder-opacity-50 min-h-[80px]"
			class:border-error={getCps(segment) > 16}
			class:bg-warning-content={isActive && false}
			contenteditable="true"
			placeholder="Transcription text..."
		/>
	</td>

	<!-- Metrics Column -->
	<td class="bg-base-100 shadow-sm align-top py-4 min-w-[120px] {isActive ? 'shadow-md' : ''}">
		<div class="flex flex-col gap-2">
			<div class="flex items-center justify-between text-xs opacity-70">
				<span>Duration</span>
				<span class="font-mono font-bold bg-base-200 px-1.5 py-0.5 rounded text-[10px]">
					{Math.round((segment.end - segment.start) * 100) / 100}s
				</span>
			</div>

			<div class="flex items-center justify-between text-xs opacity-70">
				<span>CPS</span>
				<span
					class="font-mono font-bold px-1.5 py-0.5 rounded text-[10px] {getCps(segment) > 20
						? 'bg-error text-error-content'
						: getCps(segment) > 16
							? 'bg-warning text-warning-content'
							: 'bg-success/20 text-success'}"
				>
					{getCps(segment)}
				</span>
			</div>

			{#if segment.end - segment.start > 0}
				<!-- Visual bar for duration relative to some max, e.g. 10s -->
				<progress
					class="progress progress-primary w-full h-1 opacity-20"
					value={segment.end - segment.start}
					max="10"
				></progress>
			{/if}
		</div>
	</td>

	<!-- Actions Column -->
	<td class="bg-base-100 rounded-r-2xl shadow-sm align-top py-4 pr-4 {isActive ? 'shadow-md' : ''}">
		<div
			class="flex flex-col gap-1 items-end opacity-40 group-hover:opacity-100 transition-opacity"
		>
			<!-- Insert Above -->
			<button
				on:click={() => insertSegmentAbove(index, handleHistory)}
				class="btn btn-ghost btn-xs btn-square hover:bg-base-200 hover:text-primary transition-colors tooltip tooltip-left"
				data-tip="Insert Above"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M5 10l7-7m0 0l7 7m-7-7v18"
					/></svg
				>
			</button>

			<!-- Split -->
			<button
				on:click={() => splitSegment(index, handleHistory)}
				class="btn btn-ghost btn-xs btn-square hover:bg-base-200 hover:text-info transition-colors tooltip tooltip-left"
				data-tip="Split Segment"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
					/></svg
				>
			</button>

			<!-- Insert Below -->
			<button
				on:click={() => insertSegmentBelow(index, handleHistory)}
				class="btn btn-ghost btn-xs btn-square hover:bg-base-200 hover:text-secondary transition-colors tooltip tooltip-left"
				data-tip="Insert Below"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M19 14l-7 7m0 0l-7-7m7 7V3"
					/></svg
				>
			</button>

			<div class="divider my-1 h-px bg-base-content/5 w-full"></div>

			<!-- Delete -->
			<button
				on:click={deleteSegment(index, handleHistory)}
				class="btn btn-ghost btn-xs btn-square hover:bg-error hover:text-error-content transition-colors tooltip tooltip-left text-error opacity-60 hover:opacity-100"
				data-tip="Delete Segment"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-4 h-4"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M19 7l-.867 12.142A2 2 0 0 1 16.138 21H7.862a2 2 0 0 1-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v3M4 7h16"
					/></svg
				>
			</button>
		</div>
	</td>
</tr>
