/**
 * Placeholder for future AI-powered topic and theme generation.
 * Swap the active theme provider to 'ai' once an AI backend is configured.
 *
 * @param {{ courseName: string, credits: number, modelType: string, units: Array<object> }} context
 * @returns {{ error: string }}
 */
export function generateAiThemes(_context) {
  return {
    error: 'AI topic generation is not yet enabled. Use the rules provider.',
  };
}
