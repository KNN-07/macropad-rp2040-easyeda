// Validate the real V3 definition and its parsed layout using VIA's own reader.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {
  isKeyboardDefinitionV3,
  isVIADefinitionV3,
  keyboardDefinitionV3ToVIADefinitionV3,
} = require('@the-via/reader');

const definition = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'macro12-rev-c.json'), 'utf8'),
);
assert.ok(isKeyboardDefinitionV3(definition), JSON.stringify(isKeyboardDefinitionV3.errors));
// This also validates KLE legends, switch bounds, USB identity and menu rules.
const parsed = keyboardDefinitionV3ToVIADefinitionV3(definition);
assert.ok(isVIADefinitionV3(parsed), JSON.stringify(isVIADefinitionV3.errors));
assert.equal(parsed.layouts.keys.length, 13);
assert.equal(parsed.layouts.width, 3);
assert.equal(parsed.layouts.height, 5);
assert.deepEqual(parsed.layouts.optionKeys, {});
const encoders = parsed.layouts.keys.filter((key) => key.ei !== undefined);
assert.equal(encoders.length, 1);
assert.equal(encoders[0].ei, 0);
assert.equal(encoders[0].row, 0);
assert.equal(encoders[0].col, 2);
assert.equal(encoders[0].x, 2);
assert.equal(encoders[0].y, 0);
assert.equal(parsed.vendorProductId, 0x4B4E * 65536 + 0x124C);
assert.deepEqual(parsed.menus, ['qmk_rgb_matrix']);
assert.deepEqual(parsed.keycodes, ['qmk_rgb_matrix_keycodes']);
console.log('PASS: official VIA V3 schema + conversion, 13 keys, encoder 0, 3x5 layout, RGB Matrix controls.');
