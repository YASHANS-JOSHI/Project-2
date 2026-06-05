import { generateStandardThemes } from './standardThemeStrategy.js';
import { generateMicroThemes } from './microThemeStrategy.js';
import { generateCustomThemes } from './customThemeStrategy.js';
import { generateAiThemes } from './aiThemeStrategy.js';

/** @type {Record<string, (context: object) => object>} */
const RULE_THEME_STRATEGIES = {
  standard: generateStandardThemes,
  micro: generateMicroThemes,
  custom: generateCustomThemes,
};

/** @type {'rules' | 'ai'} */
let activeThemeProvider = 'rules';

/**
 * Switches the theme generation provider.
 * Future AI integration calls setThemeProvider('ai') at startup.
 *
 * @param {'rules' | 'ai'} provider
 */
export function setThemeProvider(provider) {
  if (provider !== 'rules' && provider !== 'ai') {
    throw new Error('Theme provider must be "rules" or "ai".');
  }

  activeThemeProvider = provider;
}

/**
 * Returns the active theme provider identifier.
 *
 * @returns {'rules' | 'ai'}
 */
export function getThemeProvider() {
  return activeThemeProvider;
}

/**
 * Returns the rule-based theme strategy for a model type.
 *
 * @param {string} modelType
 * @returns {((context: object) => object) | null}
 */
export function getThemeStrategy(modelType) {
  return RULE_THEME_STRATEGIES[modelType] ?? null;
}

/**
 * Dispatches theme generation to the active provider and model strategy.
 *
 * @param {string} modelType
 * @param {object} context
 * @returns {object}
 */
export function generateThemesByModel(modelType, context) {
  if (activeThemeProvider === 'ai') {
    return generateAiThemes({ ...context, modelType });
  }

  const strategy = getThemeStrategy(modelType);

  if (!strategy) {
    return { error: `No theme strategy found for model type: ${modelType}` };
  }

  return strategy(context);
}
