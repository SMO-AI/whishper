import { transcriptions } from '$lib/stores';
import { browser, dev } from '$app/environment';
import { env } from '$env/dynamic/public';

/** @type {import('./$types').PageLoad} */
import { supabase } from '$lib/supabase';

/** @type {import('./$types').PageLoad} */
export async function load({ fetch }) {
	// Get Session
	let session = null;
	if (supabase) {
		try {
			const { data } = await supabase.auth.getSession();
			session = data?.session;
		} catch (err) {
			console.error('Error getting session:', err);
		}
	} else {
		console.warn('Supabase is not initialized');
	}

	const accessToken = session?.access_token;



	if (!accessToken) {
		return { transcriptions: [] };
	}


	// Use different endpoints for server-side and client-side
	const endpoint = browser
		? `${env.PUBLIC_API_HOST}/api/transcriptions`
		: `${env.PUBLIC_INTERNAL_API_HOST}/api/transcriptions`;

	console.log(`[SSR] Fetching transcriptions from: ${endpoint} (browser: ${browser})`);

	try {
		const response = await fetch(endpoint, {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		});

		if (response.ok) {
			const ts = await response.json();
			return { transcriptions: ts && ts.length > 0 ? ts : [] };
		} else {
			console.error('Failed to fetch transcriptions:', response.status, response.statusText);
			return { transcriptions: [] };
		}
	} catch (err) {
		console.error('Network error during SSR fetch:', err.message);
		return { transcriptions: [] };
	}


}
