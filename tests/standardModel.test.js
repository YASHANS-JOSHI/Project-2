import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  calculateUnits,
  generateUnitStructure,
  generateStandardModel,
} from '../src/models/standardModel.js';
import { validateCredits } from '../src/validation/credits.js';
import { ValidationError } from '../src/errors/ValidationError.js';

describe('validateCredits', () => {
  it('accepts positive integers', () => {
    assert.equal(validateCredits(3), 3);
    assert.equal(validateCredits(10), 10);
  });

  it('rejects zero', () => {
    assert.throws(
      () => validateCredits(0),
      (err) =>
        err instanceof ValidationError &&
        err.message.includes('greater than 0')
    );
  });

  it('rejects negative numbers', () => {
    assert.throws(() => validateCredits(-1), ValidationError);
    assert.throws(() => validateCredits(-100), ValidationError);
  });

  it('rejects null and undefined', () => {
    assert.throws(() => validateCredits(null), ValidationError);
    assert.throws(() => validateCredits(undefined), ValidationError);
  });

  it('rejects strings', () => {
    assert.throws(() => validateCredits('4'), ValidationError);
    assert.throws(() => validateCredits('abc'), ValidationError);
  });

  it('rejects non-integers', () => {
    assert.throws(() => validateCredits(3.5), ValidationError);
  });
});

describe('calculateUnits', () => {
  it('returns credits + 1', () => {
    assert.equal(calculateUnits(3), 4);
    assert.equal(calculateUnits(4), 5);
    assert.equal(calculateUnits(5), 6);
  });
});

describe('generateUnitStructure', () => {
  it('assigns 4 or 5 topics per unit', () => {
    const units = generateUnitStructure(5);

    assert.equal(units.length, 5);
    for (const unit of units) {
      assert.ok(unit.topicCount === 4 || unit.topicCount === 5);
      assert.ok(unit.unitNumber >= 1 && unit.unitNumber <= 5);
    }
  });

  it('uses alternating 5 and 4 starting at unit 1', () => {
    assert.deepEqual(generateUnitStructure(3), [
      { unitNumber: 1, topicCount: 5 },
      { unitNumber: 2, topicCount: 4 },
      { unitNumber: 3, topicCount: 5 },
    ]);
  });
});

describe('generateStandardModel', () => {
  it('generates structure for credits = 3', () => {
    const result = generateStandardModel(3);

    assert.equal(result.model, 'standard');
    assert.equal(result.credits, 3);
    assert.equal(result.totalUnits, 4);
    assert.equal(result.units.length, 4);
    assert.deepEqual(result.units[0], { unitNumber: 1, topicCount: 5 });
    assert.deepEqual(result.units[1], { unitNumber: 2, topicCount: 4 });
  });

  it('generates structure for credits = 4', () => {
    const result = generateStandardModel(4);

    assert.equal(result.model, 'standard');
    assert.equal(result.credits, 4);
    assert.equal(result.totalUnits, 5);
    assert.equal(result.units.length, 5);
    assert.equal(result.error, undefined);
  });

  it('generates structure for credits = 5', () => {
    const result = generateStandardModel(5);

    assert.equal(result.credits, 5);
    assert.equal(result.totalUnits, 6);
    assert.equal(result.units.length, 6);
    for (const unit of result.units) {
      assert.ok(unit.topicCount === 4 || unit.topicCount === 5);
    }
  });

  it('returns meaningful errors for invalid inputs', () => {
    assert.match(generateStandardModel(0).error, /greater than 0/);
    assert.ok(generateStandardModel(-2).error);
    assert.ok(generateStandardModel(null).error);
    assert.ok(generateStandardModel(undefined).error);
    assert.ok(generateStandardModel('5').error);
    assert.ok(generateStandardModel('invalid').error);
  });
});
