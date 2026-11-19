import { NextRequest, NextResponse } from 'next/server';

const AYUSH_VOICE_ID = 'HqRQSXEwwdjbY3dgUSzb'; // Ayush M - Deep Mythology Narrator
const BILL_VOICE_ID = 'pqHfZKP75CvOlQylNhV4';   // Bill - Wise, Mature, Balanced (Elderly Male Premade)

export async function POST(req: NextRequest) {
  try {
    const {
      text,
      voiceId = AYUSH_VOICE_ID,
      modelId = 'eleven_v3',
      stability = 0.0, // Creative
      similarityBoost = 0.75,
    } = await req.json();

    if (!text || typeof text !== 'string') {
      return NextResponse.json({ error: 'Text is required for TTS' }, { status: 400 });
    }

    const apiKey =
      process.env.ELEVENLABS_API_KEY ||
      'sk_f89f04ce19ba005aaee91f9498dc48d010a75e11a30d924f';
    if (!apiKey) {
      return NextResponse.json(
        { error: 'ELEVENLABS_API_KEY is not configured in server environment' },
        { status: 500 }
      );
    }

    // Helper function to call ElevenLabs TTS stream
    const synthesize = async (targetVoiceId: string) => {
      const url = `https://api.elevenlabs.io/v1/text-to-speech/${targetVoiceId}/stream`;
      return await fetch(url, {
        method: 'POST',
        headers: {
          'xi-api-key': apiKey,
          'Content-Type': 'application/json',
          Accept: 'audio/mpeg',
        },
        body: JSON.stringify({
          text,
          model_id: modelId,
          voice_settings: {
            stability,
            similarity_boost: similarityBoost,
          },
        }),
      });
    };

    let response = await synthesize(voiceId);

    // If using a library voice on a free tier, ElevenLabs returns 402/payment_required.
    // Fall back to Bill (Wise, mature elderly male doctor premade voice) seamlessly.
    if (!response.ok && (response.status === 402 || response.status === 400)) {
      const errJson = await response.json().catch(() => ({}));
      if (
        errJson?.detail?.code === 'paid_plan_required' ||
        errJson?.detail?.status === 'payment_required'
      ) {
        console.warn(
          `[ElevenLabs TTS] Library voice ${voiceId} requires paid tier. Falling back to premade doctor voice (Bill).`
        );
        response = await synthesize(BILL_VOICE_ID);
      } else {
        return NextResponse.json(
          { error: errJson?.detail?.message || 'ElevenLabs TTS failed' },
          { status: response.status }
        );
      }
    }

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `ElevenLabs TTS request failed: ${errorText}` },
        { status: response.status }
      );
    }

    // Return streaming MP3 response
    const audioStream = response.body;
    return new Response(audioStream, {
      headers: {
        'Content-Type': 'audio/mpeg',
        'Transfer-Encoding': 'chunked',
        'Cache-Control': 'no-cache',
      },
    });
  } catch (err: any) {
    console.error('[ElevenLabs TTS Route Error]:', err);
    return NextResponse.json({ error: err.message || 'Server error' }, { status: 500 });
  }
}
