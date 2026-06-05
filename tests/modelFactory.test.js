import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  getModelGenerator,
  generateByModelType,
} from '../src/models/modelFactory.js';

describe('getModelGenerator', () => {
  it('returns standard generator for "standard"', () => {
    const generator = getModelGenerator('standard');
    assert.equal(typeof generator, 'function');
    assert.equal(generator(3).model, 'standard');
  });

  it('returns micro generator for "micro"', () => {
    const generator = getModelGenerator('micro');
    assert.equal(typeof generator, 'function');
    assert.match(generator(3).error, /not yet implemented/);
  });

  it('returns custom generator for "custom"', () => {
    const generator = getModelGenerator('custom');
    assert.equal(typeof generator, 'function');
    assert.match(generator(3).error, /not yet implemented/);
  });

  it('returns null for unknown model type', () => {
    assert.equal(getModelGenerator('unknown'), null);
  });
});

describe('generateByModelType', () => {
  it('generates standard model structure', () => {
    const result = generateByModelType('standard', 4);

    assert.equal(result.model, 'standard');
    assert.equal(result.totalUnits, 5);
    assert.equal(result.units.length, 5);
  });

  it('returns error for unknown model type', () => {
    const result = generateByModelType('invalid', 3);

    assert.match(result.error, /Unknown model type/);
  });

  it('returns validation error for invalid credits', () => {
    const result = generateByModelType('standard', 0);

    assert.ok(result.error);
  });
});
