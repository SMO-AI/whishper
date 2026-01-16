<script>
	import { editorSettings } from '$lib/stores';
	import { t } from '$lib/i18n';
</script>

<div class="flex items-center gap-4 text-xs font-medium opacity-80">
	<label class="cursor-pointer flex items-center gap-2 hover:opacity-100 transition-opacity">
		<input
			bind:checked={$editorSettings.seekOnClick}
			type="checkbox"
			class="toggle toggle-xs toggle-primary"
		/>
		<span>{$t('seek_on_click')}</span>
	</label>

	<label class="cursor-pointer flex items-center gap-2 hover:opacity-100 transition-opacity">
		<input
			bind:checked={$editorSettings.autoSave}
			type="checkbox"
			class="toggle toggle-xs toggle-success"
		/>
		<span>{$t('autosave')}</span>
	</label>
</div>
