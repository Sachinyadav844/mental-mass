/**
 * Normalize Flask `success_response` payloads and Socket.IO emotion events
 * so Webcam / Monitor always receive { emotion, confidence } in a consistent shape.
 */

export type NormalizedFaceResult = {
  emotion: string;
  confidence: number;
  face_detected?: boolean;
  all_emotions?: Record<string, number>;
  source?: string;
};

function unwrapRecord(raw: unknown): Record<string, unknown> {
  if (!raw || typeof raw !== "object") return {};
  const r = raw as Record<string, unknown>;
  if (r.success === false) return r;
  if (r.data != null && typeof r.data === "object" && !Array.isArray(r.data)) {
    return r.data as Record<string, unknown>;
  }
  return r;
}

/** Map backend labels to EmotionBadge keys where names differ */
const EMOTION_ALIASES: Record<string, string> = {
  fear: "fearful",
  disgust: "disgusted",
  surprise: "surprised",
};

export function normalizeFaceAnalysisPayload(raw: unknown): NormalizedFaceResult {
  const outer = unwrapRecord(raw);
  let emotion = String(
    outer.emotion ?? (raw as Record<string, unknown>)?.emotion ?? "neutral"
  ).trim();

  const lower = emotion.toLowerCase();
  emotion = EMOTION_ALIASES[lower] ?? emotion;

  let conf: unknown =
    outer.confidence ?? (raw as Record<string, unknown>)?.confidence ?? 0;
  if (typeof conf === "string") conf = parseFloat(conf);
  let confidence = typeof conf === "number" && !Number.isNaN(conf) ? conf : 0;
  if (confidence > 1) confidence = Math.min(1, confidence / 100);

  const faceDetected = outer.face_detected;
  const allEmotions = outer.all_emotions;
  const source = outer.source;

  return {
    emotion,
    confidence,
    face_detected:
      typeof faceDetected === "boolean" ? faceDetected : undefined,
    all_emotions:
      allEmotions && typeof allEmotions === "object" && !Array.isArray(allEmotions)
        ? (allEmotions as Record<string, number>)
        : undefined,
    source: typeof source === "string" ? source : undefined,
  };
}
