import { validateCreditsResult } from '../validation/credits.js';

/** Minimum topics assigned to any unit in the Standard Model. */
const MIN_TOPICS_PER_UNIT = 4;

/** Maximum topics assigned to any unit in the Standard Model. */
const MAX_TOPICS_PER_UNIT = 5;

/**
 * Standard Model rule: total units equals credits plus one.
 *
 * @param {number} credits - Validated positive integer
 * @returns {number}
 */
export function calculateUnits(credits) {
  return credits + 1;
}

/**
 * Picks a topic count in [4, 5] for a given unit index.
 * Uses a deterministic pattern (odd units → 5, even → 4) so output is stable and testable.
 *
 * @param {number} unitNumber - 1-based unit index
 * @returns {number}
 */
function topicCountForUnit(unitNumber) {
  return unitNumber % 2 === 1 ? MAX_TOPICS_PER_UNIT : MIN_TOPICS_PER_UNIT;
}

/**
 * Builds the per-unit skeleton for the Standard Model.
 *
 * @param {number} totalUnits - Number of units to generate
 * @returns {Array<{ unitNumber: number, topicCount: number }>}
 */
export function generateUnitStructure(totalUnits) {
  const units = [];

  for (let unitNumber = 1; unitNumber <= totalUnits; unitNumber += 1) {
    units.push({
      unitNumber,
      topicCount: topicCountForUnit(unitNumber),
    });
  }

  return units;
}

/**
 * Generates a Standard Model syllabus structure from a credit count.
 *
 * @param {*} credits - Credit count (must be a positive integer)
 * @returns {object} Success payload with model metadata, or `{ error: string }` on invalid input
 */
export function generateStandardModel(credits) {
  const validation = validateCreditsResult(credits);

  if (!validation.valid) {
    return { error: validation.error };
  }

  const validatedCredits = validation.value;
  const totalUnits = calculateUnits(validatedCredits);
  const units = generateUnitStructure(totalUnits);

  return {
    model: 'standard',
    credits: validatedCredits,
    totalUnits,
    units,
  };
}
