<script>
	import { editorSettings } from '$lib/stores';
</script>

<div class="flex items-center gap-4 text-xs font-medium opacity-80">
	<label class="cursor-pointer flex items-center gap-2 hover:opacity-100 transition-opacity">
		<input
			bind:checked={$editorSettings.seekOnClick}
			type="checkbox"
			class="toggle toggle-xs toggle-primary"
		/>
		<span>Seek on click</span>
	</label>

	<label class="cursor-pointer flex items-center gap-2 hover:opacity-100 transition-opacity">
		<input
			bind:checked={$editorSettings.autoSave}
			type="checkbox"
			class="toggle toggle-xs toggle-success"
		/>
		<span>Autosave</span>
	</label>
</div>
