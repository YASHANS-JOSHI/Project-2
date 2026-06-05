import { normalizeCourseName } from '../unitPhases.js';

/**
 * Rule-based theme generation for the Custom Model.
 * Provides neutral placeholders until manual theme input is supported.
 *
 * @param {{ courseName: string, credits: number, units: Array<{ unitNumber: number, topicCount: number }> }} context
 * @returns {{ courseName: string, credits: number, modelType: string, units: Array<object> }}
 */
export function generateCustomThemes(context) {
  const normalizedName = normalizeCourseName(context.courseName);

  const units = context.units.map((unit) => ({
    unitNumber: unit.unitNumber,
    topicCount: unit.topicCount,
    unitTitle: `Custom Unit ${unit.unitNumber}: ${normalizedName}`,
    shortDescription:
      `Placeholder theme block for unit ${unit.unitNumber} of ${normalizedName}. Replace with instructor-defined themes across ${unit.topicCount} topics.`,
  }));

  return {
    courseName: normalizedName,
    credits: context.credits,
    modelType: 'custom',
    units,
  };
}
