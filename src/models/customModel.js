import { validateCreditsResult } from '../validation/credits.js';

/**
 * Placeholder for the Custom Model (Manual Input).
 * Will be implemented in a future iteration.
 *
 * @param {*} credits - Credit count
 * @returns {{ error: string }}
 */
export function generateCustomModel(credits) {
  const validation = validateCreditsResult(credits);

  if (!validation.valid) {
    return { error: validation.error };
  }

  return { error: 'Custom Model is not yet implemented.' };
}
