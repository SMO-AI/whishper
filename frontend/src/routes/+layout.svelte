<script>
	import { onMount } from 'svelte';
	import { theme, locale, transcriptions } from '$lib/stores';
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import '../app.css';

	export let data;
	$: if (data?.transcriptions) {
		transcriptions.set(data.transcriptions);
	}

	onMount(async () => {
		if (!supabase) return;

		const {
			data: { session }
		} = await supabase.auth.getSession();

		if (!session) {
			const path = window.location.pathname;
			if (path !== '/' && !path.startsWith('/auth')) {
				goto('/auth/login');
			}
		} else {
			// Check and update user metadata if needed (fixes Google Auth profile creation)
			const appMetadata = session.user.user_metadata.app;
			if (appMetadata !== 'Scriptus') {
				console.log('App metadata missing or incorrect, updating...');
				await supabase.auth.updateUser({
					data: { app: 'Scriptus' }
				});
			}

			if (window.location.pathname === '/' || window.location.pathname.startsWith('/auth')) {
				// Redirect logged-in users from public roots to app
				goto('/app');
			}
		}

		// Check for saved theme preference
		const savedTheme = localStorage.getItem('theme');
		if (savedTheme) {
			theme.set(savedTheme);
		} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
			// Default to light as per request, but respect system if needed.
			// "сделай тему светлой и интуитивно понятной" -> imply default light.
			theme.set('light');
		}

		// Subscribe to theme changes
		theme.subscribe((value) => {
			if (typeof document !== 'undefined') {
				document.documentElement.setAttribute('data-theme', value);
				localStorage.setItem('theme', value);
			}
		});

		// Locale persistence
		const savedLocale = localStorage.getItem('locale');
		if (savedLocale) {
			locale.set(savedLocale);
		}

		locale.subscribe((value) => {
			if (typeof document !== 'undefined') {
				localStorage.setItem('locale', value);
			}
		});
	});
</script>

<div class="min-h-screen bg-base-100 text-base-content transition-colors duration-200">
	<slot />
</div>
