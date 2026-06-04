/**
 * Thrown when syllabus input fails validation.
 * Shared across Standard, Micro, and Custom models.
 */
export class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
  }
}
