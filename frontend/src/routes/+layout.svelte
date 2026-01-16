<script>
	import { onMount } from 'svelte';
	import { theme } from '$lib/stores';
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import '../app.css';

	onMount(async () => {
		const {
			data: { session }
		} = await supabase.auth.getSession();

		if (!session) {
			const path = window.location.pathname;
			if (!path.startsWith('/auth')) {
				goto('/auth/login');
			}
		} else if (window.location.pathname === '/' || window.location.pathname.startsWith('/auth')) {
			// Redirect logged-in users from public roots to app
			goto('/app');
		}

		// Check for saved theme preference
		const savedTheme = localStorage.getItem('theme');
		if (savedTheme) {
			theme.set(savedTheme);
		} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
			// Default to light as per request, but respect system if needed.
			// User explicitly asked for light to be intuitive/default for non-tech users?
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
	});
</script>

<div class="min-h-screen bg-base-100 text-base-content transition-colors duration-200">
	<slot />
</div>
