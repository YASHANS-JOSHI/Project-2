import { ValidationError } from '../errors/ValidationError.js';

/**
 * Validates the credits input used by all syllabus models.
 *
 * @param {*} credits - Proposed credit count
 * @returns {number} Validated positive integer credits
 * @throws {ValidationError} When credits is missing, non-numeric, non-integer, or <= 0
 */
export function validateCredits(credits) {
  if (credits === null || credits === undefined) {
    throw new ValidationError(
      'Credits is required and cannot be null or undefined.'
    );
  }

  if (typeof credits === 'string') {
    throw new ValidationError('Credits must be a number, not a string.');
  }

  if (typeof credits !== 'number' || Number.isNaN(credits)) {
    throw new ValidationError('Credits must be a valid number.');
  }

  if (!Number.isInteger(credits)) {
    throw new ValidationError('Credits must be a whole number (integer).');
  }

  if (credits <= 0) {
    throw new ValidationError('Credits must be greater than 0.');
  }

  return credits;
}

/**
 * Non-throwing validation for callers that prefer a result object.
 *
 * @param {*} credits
 * @returns {{ valid: true, value: number } | { valid: false, error: string }}
 */
export function validateCreditsResult(credits) {
  try {
    return { valid: true, value: validateCredits(credits) };
  } catch (error) {
    if (error instanceof ValidationError) {
      return { valid: false, error: error.message };
    }
    throw error;
  }
}
