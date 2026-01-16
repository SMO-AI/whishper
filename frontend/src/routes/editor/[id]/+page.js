/** @type {import('./$types').PageLoad} */
import { currentTranscription } from '$lib/stores';
import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';
import { supabase } from '$lib/supabase';

export async function load({ params, fetch }) {
	let id = params.id;

	// Use different endpoints for server-side and client-side
	const endpoint = browser
		? `${env.PUBLIC_API_HOST}/api/transcriptions`
		: `${env.PUBLIC_INTERNAL_API_HOST}/api/transcriptions`;

	// Get Token
	let accessToken = null;
	if (supabase) {
		const { data } = await supabase.auth.getSession();
		accessToken = data?.session?.access_token;
	}

	try {
		const response = await fetch(`${endpoint}/${id}`, {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		});

		if (response.ok) {
			const ts = await response.json();
			// Set currentTranscription to the fetched transcription
			currentTranscription.set(ts);
			return { transcription: ts };
		} else {
			console.error(`Failed to fetch transcription for editor (${id}):`, response.status);
			return { error: 'Unauthorized', transcription: null };
		}
	} catch (err) {
		console.error('Network error fetching transcription for editor:', err);
		return { error: 'Network Error', transcription: null };
	}
}
