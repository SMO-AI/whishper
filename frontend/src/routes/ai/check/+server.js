import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export async function POST({ request }) {
    const { segments } = await request.json();
    const apiKey = env.GROQ_API_KEY;

    if (!apiKey) {
        return json({ error: 'Groq API Key missing' }, { status: 500 });
    }

    // Prepare segments for the prompt to save tokens (only ID and text)
    const segmentsToProcess = segments.map((s) => ({ id: s.id, text: s.text }));

    // Basic batching strategy: 
    // If we have many segments, we might need to loop. 
    // For now, let's assume reasonable length or that the user processes in chunks?
    // But the requirement is "reads all text".
    // Let's try to process in batches of 50 to avoid context limits.

    const BATCH_SIZE = 50;
    let allCorrections = {};

    for (let i = 0; i < segmentsToProcess.length; i += BATCH_SIZE) {
        const batch = segmentsToProcess.slice(i, i + BATCH_SIZE);

        const systemPrompt = `You are an expert copy editor. Your task is to identify and fix spelling, grammar, and punctuation errors in the provided text segments.
Input is a JSON array: [{ "id": "...", "text": "..." }].
Output MUST be a valid JSON object where keys are the segment IDs and values are the CORRECTED text.
ONLY include segments that actually contain errors. If a segment is correct, DO NOT include it in the output.
Do not change style or meaning, only fix objective errors.`;

        try {
            const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: 'llama-3.3-70b-versatile',
                    messages: [
                        { role: 'system', content: systemPrompt },
                        { role: 'user', content: JSON.stringify(batch) }
                    ],
                    response_format: { type: "json_object" },
                    temperature: 0.1
                })
            });

            if (!response.ok) {
                const err = await response.text();
                console.error('Groq API Error:', err);
                continue; // Try next batch or fail? For now continue
            }

            const data = await response.json();
            const content = data.choices[0].message.content;
            try {
                const batchCorrections = JSON.parse(content);
                allCorrections = { ...allCorrections, ...batchCorrections };
            } catch (parseError) {
                console.error('JSON Parse Error:', parseError);
            }

        } catch (e) {
            console.error('Error processing batch:', e);
        }
    }

    return json({ corrections: allCorrections });
}
