import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  generateUnitThemes,
  validateRuleEngineInput,
  resolveUnitPhase,
  setThemeProvider,
  getThemeProvider,
} from '../src/ruleEngine/index.js';

const sampleUnits = [
  { unitNumber: 1, topicCount: 5 },
  { unitNumber: 2, topicCount: 4 },
  { unitNumber: 3, topicCount: 5 },
  { unitNumber: 4, topicCount: 4 },
];

describe('validateRuleEngineInput', () => {
  it('accepts valid input', () => {
    const value = validateRuleEngineInput({
      courseName: 'Data Structures',
      credits: 3,
      modelType: 'standard',
      units: sampleUnits,
    });

    assert.equal(value.courseName, 'Data Structures');
    assert.equal(value.credits, 3);
    assert.equal(value.modelType, 'standard');
    assert.equal(value.units.length, 4);
  });

  it('rejects missing courseName', () => {
    assert.throws(
      () =>
        validateRuleEngineInput({
          courseName: '',
          credits: 3,
          modelType: 'standard',
          units: sampleUnits,
        }),
      /courseName is required/
    );
  });

  it('rejects invalid credits', () => {
    assert.throws(
      () =>
        validateRuleEngineInput({
          courseName: 'Physics',
          credits: 0,
          modelType: 'standard',
          units: sampleUnits,
        }),
      /greater than 0/
    );
  });

  it('rejects invalid modelType', () => {
    assert.throws(
      () =>
        validateRuleEngineInput({
          courseName: 'Physics',
          credits: 3,
          modelType: 'invalid',
          units: sampleUnits,
        }),
      /modelType is required/
    );
  });

  it('rejects empty units array', () => {
    assert.throws(
      () =>
        validateRuleEngineInput({
          courseName: 'Physics',
          credits: 3,
          modelType: 'standard',
          units: [],
        }),
      /non-empty array/
    );
  });

  it('rejects invalid unit entries', () => {
    assert.throws(
      () =>
        validateRuleEngineInput({
          courseName: 'Physics',
          credits: 3,
          modelType: 'standard',
          units: [{ unitNumber: 0, topicCount: 4 }],
        }),
      /positive integer unitNumber/
    );
  });
});

describe('resolveUnitPhase', () => {
  it('returns introduction for the first unit', () => {
    assert.equal(resolveUnitPhase(1, 4), 'introduction');
  });

  it('returns synthesis for the last unit', () => {
    assert.equal(resolveUnitPhase(4, 4), 'synthesis');
  });

  it('returns middle phases for intermediate units', () => {
    assert.equal(resolveUnitPhase(2, 4), 'core');
    assert.equal(resolveUnitPhase(3, 4), 'advanced');
  });
});

describe('generateUnitThemes', () => {
  it('generates themed units for the standard model', () => {
    const result = generateUnitThemes({
      courseName: 'data structures',
      credits: 3,
      modelType: 'standard',
      units: sampleUnits,
    });

    assert.equal(result.modelType, 'standard');
    assert.equal(result.courseName, 'Data structures');
    assert.equal(result.totalUnits, 4);
    assert.equal(result.units.length, 4);
    assert.match(result.units[0].unitTitle, /Introduction to Data structures/);
    assert.ok(result.units[0].shortDescription.length > 0);
    assert.equal(result.units[0].topicCount, 5);
    assert.equal(result.error, undefined);
  });

  it('generates themed units for the micro model', () => {
    const result = generateUnitThemes({
      courseName: 'Operating Systems',
      credits: 2,
      modelType: 'micro',
      units: sampleUnits.slice(0, 2),
    });

    assert.equal(result.modelType, 'micro');
    assert.match(result.units[0].unitTitle, /Learning Module 1/);
  });

  it('generates themed units for the custom model', () => {
    const result = generateUnitThemes({
      courseName: 'Ethics',
      credits: 1,
      modelType: 'custom',
      units: [{ unitNumber: 1, topicCount: 4 }],
    });

    assert.equal(result.modelType, 'custom');
    assert.match(result.units[0].unitTitle, /Custom Unit 1/);
  });

  it('returns validation errors without throwing', () => {
    const result = generateUnitThemes({
      courseName: '',
      credits: 3,
      modelType: 'standard',
      units: sampleUnits,
    });

    assert.ok(result.error);
  });

  it('uses AI provider when configured', () => {
    const previous = getThemeProvider();
    setThemeProvider('ai');

    const result = generateUnitThemes({
      courseName: 'Algorithms',
      credits: 3,
      modelType: 'standard',
      units: sampleUnits,
    });

    setThemeProvider(previous);

    assert.match(result.error, /AI topic generation is not yet enabled/);
  });
});
