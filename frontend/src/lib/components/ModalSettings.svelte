<script>
	import { supabase } from '$lib/supabase';
	import toast from 'svelte-french-toast';
	import { onMount } from 'svelte';
	import { locale, t } from '$lib/stores';

	import { writable } from 'svelte/store';

	export let show = false;

	let activeTab = 'profile'; // 'profile' or 'settings'
	let loading = false;

	// Profile data
	let profile = {
		full_name: '',
		avatar_url: '',
		email: '',
		bio: ''
	};
	let newPassword = '';
	let avatarFile;
	let avatarPreview;

	export function showModal(tab = 'profile') {
		activeTab = tab;
		document.getElementById('modal_settings').showModal();
		loadProfile();
	}

	async function loadProfile() {
		const {
			data: { session }
		} = await supabase.auth.getSession();
		if (session) {
			profile.email = session.user.email;
			// Try to fetch from whishper_profiles first
			const { data: dbProfile, error } = await supabase
				.from('whishper_profiles')
				.select('*')
				.eq('id', session.user.id)
				.single();

			if (dbProfile) {
				profile.full_name = dbProfile.name || session.user.user_metadata.full_name || '';
				profile.avatar_url = dbProfile.avatar_image || session.user.user_metadata.avatar_url || '';
				profile.bio = dbProfile.bio || '';
				// Sync email if different? Usually auth email is source of truth.
				profile.email = session.user.email;
			} else {
				// Fallback to auth metadata
				profile.full_name = session.user.user_metadata.full_name || '';
				profile.avatar_url = session.user.user_metadata.avatar_url || '';
				profile.bio = '';
			}
		}
	}

	async function updateProfile() {
		loading = true;
		try {
			const {
				data: { session }
			} = await supabase.auth.getSession();
			if (!session) throw new Error('No session');

			const updates = {
				full_name: profile.full_name,
				updated_at: new Date()
			};

			// Updates for whishper_profiles table
			const dbUpdates = {
				name: profile.full_name,
				bio: profile.bio,
				email: session.user.email, // Ensure email is synced
				updated_at: new Date()
			};

			if (avatarFile) {
				const fileExt = avatarFile.name.split('.').pop();
				const fileName = `${Math.random()}.${fileExt}`;
				const { error: uploadError } = await supabase.storage
					.from('avatars')
					.upload(fileName, avatarFile);

				if (uploadError) throw uploadError;

				const {
					data: { publicUrl }
				} = supabase.storage.from('avatars').getPublicUrl(fileName);

				updates.avatar_url = publicUrl;
				dbUpdates.avatar_image = publicUrl;
			}

			// 1. Update Supabase Auth Table (Metadata)
			const { error } = await supabase.auth.updateUser({
				data: updates
			});
			if (error) throw error;

			// 2. Update whishper_profiles Table
			const { error: dbError } = await supabase
				.from('whishper_profiles')
				.update(dbUpdates)
				.eq('id', session.user.id);

			if (dbError) throw dbError;

			// 3. Update Password if provided
			if (newPassword) {
				const { error: pwdError } = await supabase.auth.updateUser({
					password: newPassword
				});
				if (pwdError) throw pwdError;
			}

			toast.success($t('success_profile_updated'));
			document.getElementById('modal_settings').close();
		} catch (error) {
			console.error(error);
			toast.error(error.message);
		} finally {
			loading = false;
		}
	}

	function handleAvatarChange(e) {
		const file = e.target.files[0];
		if (file) {
			avatarFile = file;
			const reader = new FileReader();
			reader.onload = (e) => (avatarPreview = e.target.result);
			reader.readAsDataURL(file);
		}
	}

	function setLanguage(lang) {
		locale.set(lang);
		// Persist preference
		if (typeof window !== 'undefined') {
			localStorage.setItem('locale', lang);
		}
	}
</script>

<dialog id="modal_settings" class="modal">
	<div class="modal-box w-11/12 max-w-2xl bg-base-100 p-0 overflow-hidden relative">
		<!-- Close Button -->
		<form method="dialog">
			<button class="btn btn-sm btn-circle btn-ghost absolute right-4 top-4 z-50">✕</button>
		</form>

		<div class="flex h-[500px]">
			<!-- Sidebar -->
			<div class="w-1/3 bg-base-200 p-6 flex flex-col gap-2">
				<h3 class="text-xl font-bold mb-6 px-2">{$t('settings')}</h3>

				<button
					class="btn btn-ghost justify-start gap-3 {activeTab === 'profile' ? 'bg-base-300' : ''}"
					on:click={() => (activeTab = 'profile')}
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
							d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
						/></svg
					>
					{$t('profile')}
				</button>

				<button
					class="btn btn-ghost justify-start gap-3 {activeTab === 'settings' ? 'bg-base-300' : ''}"
					on:click={() => (activeTab = 'settings')}
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
							d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
						/><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
						/></svg
					>
					{$t('general')}
				</button>

				<div class="mt-auto">
					<button
						class="btn btn-ghost text-error justify-start gap-3 w-full"
						on:click={() => supabase.auth.signOut()}
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
								d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
							/></svg
						>
						{$t('logout')}
					</button>
				</div>
			</div>

			<!-- Content -->
			<div class="flex-1 p-8 overflow-y-auto">
				{#if activeTab === 'profile'}
					<div class="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
						<h2 class="text-2xl font-bold">{$t('edit_profile')}</h2>

						<!-- Avatar -->
						<div class="flex items-center gap-6">
							<div class="avatar">
								<div class="w-24 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
									<img
										src={avatarPreview ||
											profile.avatar_url ||
											`https://ui-avatars.com/api/?name=${profile.full_name}`}
										alt="avatar"
									/>
								</div>
							</div>
							<div class="flex flex-col gap-2">
								<label class="btn btn-outline btn-sm">
									{$t('upload_avatar')}
									<input
										type="file"
										accept="image/*"
										class="hidden"
										on:change={handleAvatarChange}
									/>
								</label>
								<p class="text-xs opacity-60">JPG, PNG or GIF. Max 5MB.</p>
							</div>
						</div>

						<!-- Form -->
						<div class="form-control w-full">
							<label class="label">
								<span class="label-text">{$t('email')}</span>
							</label>
							<input
								type="text"
								value={profile.email}
								readonly
								class="input input-bordered w-full opacity-60 cursor-not-allowed"
							/>
						</div>

						<div class="form-control w-full">
							<label class="label">
								<span class="label-text">{$t('full_name')}</span>
							</label>
							<input
								type="text"
								bind:value={profile.full_name}
								class="input input-bordered w-full"
							/>
						</div>

						<div class="form-control w-full">
							<label class="label">
								<span class="label-text">{$t('bio')}</span>
							</label>
							<textarea
								bind:value={profile.bio}
								class="textarea textarea-bordered h-24"
								placeholder={$t('bio_placeholder')}
							/>
						</div>

						<div class="form-control w-full">
							<label class="label">
								<span class="label-text">{$t('new_password')}</span>
							</label>
							<input
								type="password"
								bind:value={newPassword}
								placeholder="••••••••"
								class="input input-bordered w-full"
							/>
						</div>

						<div class="flex justify-end pt-4">
							<button class="btn btn-primary" on:click={updateProfile} disabled={loading}>
								{#if loading}
									<span class="loading loading-spinner" />
								{/if}
								{$t('save')}
							</button>
						</div>
					</div>
				{:else if activeTab === 'settings'}
					<div class="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
						<h2 class="text-2xl font-bold">{$t('general')}</h2>

						<div class="form-control w-full max-w-xs">
							<label class="label">
								<span class="label-text">{$t('language')}</span>
							</label>
							<select
								class="select select-bordered"
								value={$locale}
								on:change={(e) => setLanguage(e.target.value)}
							>
								<option value="ru">Русский</option>
								<option value="en">English</option>
							</select>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</dialog>
