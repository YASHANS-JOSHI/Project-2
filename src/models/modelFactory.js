import { generateStandardModel } from './standardModel.js';
import { generateMicroUnitModel } from './microUnitModel.js';
import { generateCustomModel } from './customModel.js';

/** @type {Record<string, (credits: *) => object>} */
const MODEL_GENERATORS = {
  standard: generateStandardModel,
  micro: generateMicroUnitModel,
  custom: generateCustomModel,
};

/**
 * Returns the generator function for a given model type.
 *
 * @param {string} modelType - One of: 'standard', 'micro', 'custom'
 * @returns {((credits: *) => object) | null}
 */
export function getModelGenerator(modelType) {
  return MODEL_GENERATORS[modelType] ?? null;
}

/**
 * Dispatches credit-based generation to the appropriate model generator.
 *
 * @param {string} modelType - One of: 'standard', 'micro', 'custom'
 * @param {*} credits - Credit count passed to the selected generator
 * @returns {object} Generated structure or `{ error: string }`
 */
export function generateByModelType(modelType, credits) {
  const generator = getModelGenerator(modelType);

  if (!generator) {
    return { error: `Unknown model type: ${modelType}` };
  }

  return generator(credits);
}
