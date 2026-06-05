import {
  normalizeCourseName,
  resolveUnitPhase,
  UNIT_PHASES,
} from '../unitPhases.js';

/**
 * Rule-based theme generation for the Standard Model.
 *
 * @param {{ courseName: string, credits: number, units: Array<{ unitNumber: number, topicCount: number }> }} context
 * @returns {{ courseName: string, credits: number, modelType: string, units: Array<object> }}
 */
export function generateStandardThemes(context) {
  const normalizedName = normalizeCourseName(context.courseName);
  const totalUnits = context.units.length;

  const units = context.units.map((unit) => {
    const phaseKey = resolveUnitPhase(unit.unitNumber, totalUnits);
    const phase = UNIT_PHASES[phaseKey];

    return {
      unitNumber: unit.unitNumber,
      topicCount: unit.topicCount,
      unitTitle: phase.title(normalizedName),
      shortDescription: phase.description(normalizedName, unit.topicCount),
    };
  });

  return {
    courseName: normalizedName,
    credits: context.credits,
    modelType: 'standard',
    units,
  };
}
