import { transcriptions } from '$lib/stores';
import { browser, dev } from '$app/environment';
import { env } from '$env/dynamic/public';

/** @type {import('./$types').PageLoad} */
import { supabase } from '$lib/supabase';

/** @type {import('./$types').PageLoad} */
export async function load({ fetch }) {
	// Get Session
	const {
		data: { session }
	} = await supabase.auth.getSession();
	const accessToken = session?.access_token;

	if (!accessToken) {
		transcriptions.update((_) => []);
		return;
	}

	// Use different endpoints for server-side and client-side
	const endpoint = browser
		? `${env.PUBLIC_API_HOST}/api/transcriptions`
		: `${env.PUBLIC_INTERNAL_API_HOST}/api/transcriptions`;

	const response = await fetch(endpoint, {
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	});

	if (response.ok) {
		const ts = await response.json();
		transcriptions.update((_) => (ts && ts.length > 0 ? ts : []));
	} else {
		transcriptions.update((_) => []);
	}
}
