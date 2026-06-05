import { generateUnitThemes } from './ruleEngine/index.js';

/**
 * CLI entry point for the Rule Engine.
 * Reads JSON from stdin:
 * {
 *   "courseName": "Data Structures",
 *   "credits": 3,
 *   "modelType": "standard",
 *   "units": [{ "unitNumber": 1, "topicCount": 5 }]
 * }
 */
async function main() {
  const chunks = [];

  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }

  try {
    const input = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    const result = generateUnitThemes(input);

    console.log(JSON.stringify(result));

    if (result.error) {
      process.exit(1);
    }
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
    process.exit(1);
  }
}

main();
