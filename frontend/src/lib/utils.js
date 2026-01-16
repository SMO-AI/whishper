import { transcriptions } from './stores';
import { dev } from '$app/environment';
import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';

export let CLIENT_API_HOST = browser
	? `${dev ? env.PUBLIC_API_HOST : ''}`
	: `${env.PUBLIC_INTERNAL_API_HOST}`;
export let CLIENT_WS_HOST = browser
	? `${dev ? env.PUBLIC_API_HOST.replace('http://', '').replace('https://', '') : ''}`
	: `${dev ? env.PUBLIC_INTERNAL_API_HOST.replace('http://', '').replace('https://', '') : ''}`;

// URL Validator
export const validateURL = function (url) {
	try {
		new URL(url);
		return true;
	} catch (e) {
		return false;
	}
};

import { supabase } from '$lib/supabase';

export const deleteTranscription = async function (id) {
	const {
		data: { session }
	} = await supabase.auth.getSession();
	const accessToken = session?.access_token;

	if (!accessToken) return;

	const res = await fetch(`${CLIENT_API_HOST}/api/transcriptions/${id}`, {
		method: 'DELETE',
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	});

	if (res.ok) {
		transcriptions.update((_transcriptions) => _transcriptions.filter((t) => t.id !== id));
	}
};

export const getRandomSentence = function () {
	const sentences = [
		'quote_1',
		'quote_2',
		'quote_3',
		'quote_4',
		'quote_5',
		'quote_6',
		'quote_7',
		'quote_8',
		'quote_9',
		'quote_10',
		'quote_11',
		'quote_12',
		'quote_13',
		'quote_14',
		'quote_15',
		'quote_16',
		'quote_17'
	];

	const randomSentence = sentences[Math.floor(Math.random() * sentences.length)];

	return randomSentence;
};

// Expects a segments array with start, end and text properties
export const downloadSRT = function (jsonData, title) {
	let srtContent = '';

	jsonData.forEach((segment, index) => {
		let startSeconds = Math.floor(segment.start);
		let startMillis = Math.floor((segment.start - startSeconds) * 1000);
		let start = new Date(startSeconds * 1000 + startMillis).toISOString().substr(11, 12);
		let endSeconds = Math.floor(segment.end);
		let endMillis = Math.floor((segment.end - endSeconds) * 1000);
		let end = new Date(endSeconds * 1000 + endMillis).toISOString().substr(11, 12);

		srtContent += `${index + 1}\n${start} --> ${end}\n${segment.text}\n\n`;
	});

	let srtBlob = new Blob([srtContent], { type: 'text/plain' });
	let url = URL.createObjectURL(srtBlob);
	let link = document.createElement('a');
	link.href = url;
	link.download = `${title}.srt`;
	link.click();
};

// Downloads received text as a TXT file
export const downloadTXT = function (text, title) {
	let srtBlob = new Blob([text], { type: 'text/plain' });
	let url = URL.createObjectURL(srtBlob);
	let link = document.createElement('a');
	link.href = url;
	link.download = `${title}.txt`;
	link.click();
};

// Downloads received JSON data as a JSON file
export const downloadJSON = function (jsonData, title) {
	let srtBlob = new Blob([JSON.stringify(jsonData)], { type: 'text/plain' });
	let url = URL.createObjectURL(srtBlob);
	let link = document.createElement('a');
	link.href = url;
	link.download = `${title}.json`;
	link.click();
};

// Expects a segments array with start, end and text properties
export const downloadVTT = function (jsonData, title) {
	let vttContent = 'WEBVTT\n\n'; // VTT files start with "WEBVTT" line

	jsonData.forEach((segment, index) => {
		let startSeconds = Math.floor(segment.start);
		let startMillis = Math.floor((segment.start - startSeconds) * 1000);
		let start = new Date(startSeconds * 1000 + startMillis).toISOString().substr(11, 12);

		let endSeconds = Math.floor(segment.end);
		let endMillis = Math.floor((segment.end - endSeconds) * 1000);
		let end = new Date(endSeconds * 1000 + endMillis).toISOString().substr(11, 12);

		vttContent += `${index + 1}\n${start} --> ${end}\n${segment.text}\n\n`;
	});

	let vttBlob = new Blob([vttContent], { type: 'text/plain' });
	let url = URL.createObjectURL(vttBlob);
	let link = document.createElement('a');
	link.href = url;
	link.download = `${title}.vtt`;
	link.click();
};
