import { generateByModelType } from './models/modelFactory.js';

/**
 * CLI entry point for external callers (e.g. Python/Streamlit via subprocess).
 * Reads JSON from stdin: { "modelType": "standard", "credits": 3 }
 * Writes JSON result to stdout.
 */
async function main() {
  const chunks = [];

  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }

  try {
    const input = JSON.parse(Buffer.concat(chunks).toString('utf8'));

    if (!input.modelType) {
      console.log(JSON.stringify({ error: 'modelType is required.' }));
      process.exit(1);
    }

    const result = generateByModelType(input.modelType, input.credits);
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
