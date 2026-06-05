import { normalizeCourseName } from '../unitPhases.js';

/**
 * Rule-based theme generation for the Micro-Unit Model (LMS style).
 * Uses compact module-oriented titles until full micro-unit rules are defined.
 *
 * @param {{ courseName: string, credits: number, units: Array<{ unitNumber: number, topicCount: number }> }} context
 * @returns {{ courseName: string, credits: number, modelType: string, units: Array<object> }}
 */
export function generateMicroThemes(context) {
  const normalizedName = normalizeCourseName(context.courseName);

  const units = context.units.map((unit) => ({
    unitNumber: unit.unitNumber,
    topicCount: unit.topicCount,
    unitTitle: `Learning Module ${unit.unitNumber}: ${normalizedName}`,
    shortDescription:
      `Micro-unit ${unit.unitNumber} for ${normalizedName} with ${unit.topicCount} bite-sized learning topics designed for LMS delivery.`,
  }));

  return {
    courseName: normalizedName,
    credits: context.credits,
    modelType: 'micro',
    units,
  };
}
