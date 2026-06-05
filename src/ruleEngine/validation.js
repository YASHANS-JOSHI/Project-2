import { ValidationError } from '../errors/ValidationError.js';
import { validateCreditsResult } from '../validation/credits.js';

const VALID_MODEL_TYPES = new Set(['standard', 'micro', 'custom']);

/**
 * Validates a single unit structure entry from the model engine.
 *
 * @param {*} unit
 * @param {number} index - 0-based index for error messages
 */
function validateUnitStructureEntry(unit, index) {
  if (!unit || typeof unit !== 'object') {
    throw new ValidationError(`Unit at index ${index} must be an object.`);
  }

  if (!Number.isInteger(unit.unitNumber) || unit.unitNumber <= 0) {
    throw new ValidationError(
      `Unit at index ${index} must have a positive integer unitNumber.`
    );
  }

  if (!Number.isInteger(unit.topicCount) || unit.topicCount <= 0) {
    throw new ValidationError(
      `Unit at index ${index} must have a positive integer topicCount.`
    );
  }
}

/**
 * Validates Rule Engine input.
 *
 * @param {*} input
 * @returns {{ courseName: string, credits: number, modelType: string, units: Array<{ unitNumber: number, topicCount: number }> }}
 * @throws {ValidationError}
 */
export function validateRuleEngineInput(input) {
  if (!input || typeof input !== 'object') {
    throw new ValidationError('Rule Engine input must be an object.');
  }

  if (typeof input.courseName !== 'string' || !input.courseName.trim()) {
    throw new ValidationError('courseName is required and must be a non-empty string.');
  }

  const creditsValidation = validateCreditsResult(input.credits);

  if (!creditsValidation.valid) {
    throw new ValidationError(creditsValidation.error);
  }

  if (typeof input.modelType !== 'string' || !VALID_MODEL_TYPES.has(input.modelType)) {
    throw new ValidationError(
      'modelType is required and must be one of: standard, micro, custom.'
    );
  }

  if (!Array.isArray(input.units) || input.units.length === 0) {
    throw new ValidationError('units is required and must be a non-empty array.');
  }

  input.units.forEach(validateUnitStructureEntry);

  return {
    courseName: input.courseName.trim(),
    credits: creditsValidation.value,
    modelType: input.modelType,
    units: input.units.map((unit) => ({
      unitNumber: unit.unitNumber,
      topicCount: unit.topicCount,
    })),
  };
}

/**
 * Non-throwing validation wrapper for Rule Engine input.
 *
 * @param {*} input
 * @returns {{ valid: true, value: object } | { valid: false, error: string }}
 */
export function validateRuleEngineInputResult(input) {
  try {
    return { valid: true, value: validateRuleEngineInput(input) };
  } catch (error) {
    if (error instanceof ValidationError) {
      return { valid: false, error: error.message };
    }

    throw error;
  }
}
