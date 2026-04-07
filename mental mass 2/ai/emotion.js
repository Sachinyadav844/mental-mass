export const detectEmotion = (image) => {
  const emotions = ["happy", "neutral", "sad", "surprised", "angry"];
  const emotion = emotions[Math.floor(Math.random() * emotions.length)];
  return { emotion, confidence: 0.7 + Math.random() * 0.3 };
};

export const analyzeSentiment = (text) => {
  const sentiments = ["positive", "negative", "neutral"];
  const sentiment = sentiments[Math.floor(Math.random() * sentiments.length)];
  const score = Math.random();
  const keywords = ["stress", "happiness", "anxiety"];
  return { sentiment, score, keywords };
};