/**
 * Pedagogical phase definitions used by rule-based theme generation.
 * Each phase supplies title and description patterns for a unit position.
 */

/** @type {Record<string, { title: (courseName: string) => string, description: (courseName: string, topicCount: number) => string }>} */
export const UNIT_PHASES = {
  introduction: {
    title: (courseName) => `Introduction to ${courseName}`,
    description: (courseName, topicCount) =>
      `Provides an overview of ${courseName}, establishing scope, key terminology, and learning objectives across ${topicCount} introductory topics.`,
  },
  foundations: {
    title: (courseName) => `Foundations of ${courseName}`,
    description: (courseName, topicCount) =>
      `Builds essential prerequisite knowledge for ${courseName}, covering ${topicCount} foundational topics that support deeper study.`,
  },
  core: {
    title: (courseName) => `Core Concepts in ${courseName}`,
    description: (courseName, topicCount) =>
      `Explores central theories and methods of ${courseName} through ${topicCount} focused topics forming the course backbone.`,
  },
  applications: {
    title: (courseName) => `Applications of ${courseName}`,
    description: (courseName, topicCount) =>
      `Examines practical use cases and problem-solving approaches in ${courseName} across ${topicCount} applied topics.`,
  },
  advanced: {
    title: (courseName) => `Advanced Topics in ${courseName}`,
    description: (courseName, topicCount) =>
      `Covers specialized and in-depth areas of ${courseName} through ${topicCount} advanced topics for extended mastery.`,
  },
  synthesis: {
    title: (courseName) => `Integration and Synthesis in ${courseName}`,
    description: (courseName, topicCount) =>
      `Integrates prior learning in ${courseName}, connecting ${topicCount} topics into a cohesive understanding of the subject.`,
  },
};

/**
 * Resolves the pedagogical phase for a unit based on its position in the syllabus.
 *
 * @param {number} unitNumber - 1-based unit index
 * @param {number} totalUnits - Total number of units
 * @returns {keyof typeof UNIT_PHASES}
 */
export function resolveUnitPhase(unitNumber, totalUnits) {
  if (totalUnits <= 1) {
    return 'introduction';
  }

  if (unitNumber === 1) {
    return 'introduction';
  }

  if (unitNumber === totalUnits) {
    return 'synthesis';
  }

  if (totalUnits === 2) {
    return 'synthesis';
  }

  const middleIndex = unitNumber - 1;
  const middleTotal = totalUnits - 2;
  const ratio = middleTotal > 0 ? middleIndex / middleTotal : 0;

  if (ratio <= 0.34) {
    return 'foundations';
  }

  if (ratio <= 0.67) {
    return 'core';
  }

  if (unitNumber === totalUnits - 1 && totalUnits > 3) {
    return 'advanced';
  }

  return 'applications';
}

/**
 * Normalizes a course name for display in generated titles.
 *
 * @param {string} courseName
 * @returns {string}
 */
export function normalizeCourseName(courseName) {
  const trimmed = courseName.trim().replace(/\s+/g, ' ');
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}
