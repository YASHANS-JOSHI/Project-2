import { validateRuleEngineInputResult } from './validation.js';
import { generateThemesByModel } from './themeStrategies/index.js';

/**
 * Rule Engine entry point.
 * Enriches a generated unit structure with meaningful unit titles and descriptions.
 *
 * @param {object} input
 * @param {string} input.courseName
 * @param {number} input.credits
 * @param {string} input.modelType - 'standard' | 'micro' | 'custom'
 * @param {Array<{ unitNumber: number, topicCount: number }>} input.units
 * @returns {object} Themed syllabus payload or `{ error: string }`
 */
export function generateUnitThemes(input) {
  const validation = validateRuleEngineInputResult(input);

  if (!validation.valid) {
    return { error: validation.error };
  }

  const { courseName, credits, modelType, units } = validation.value;

  const result = generateThemesByModel(modelType, {
    courseName,
    credits,
    units,
  });

  if (result.error) {
    return result;
  }

  return {
    ...result,
    totalUnits: units.length,
  };
}

export { validateRuleEngineInput, validateRuleEngineInputResult } from './validation.js';
export {
  getThemeStrategy,
  getThemeProvider,
  setThemeProvider,
  generateThemesByModel,
} from './themeStrategies/index.js';
export { generateAiThemes } from './themeStrategies/aiThemeStrategy.js';
export {
  normalizeCourseName,
  resolveUnitPhase,
  UNIT_PHASES,
} from './unitPhases.js';
