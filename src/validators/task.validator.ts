import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { TaskCreateInput, TaskUpdateInput } from '../types/task.types.js';

/* LLM_SECTION_START */
// Entity: Task
// Fields (name: ts_type, required/optional):
//   title: string (required)
//   description: string (optional)
//   status: string (required)
//   priority: number (required)
//   projectId: number (required)
//   assigneeId: number (optional)
//   createdAt: Date (required)
//   updatedAt: Date (required)
// TODO: define Zod schemas for Task create and update
// PARENT-FK: projectId is required in the request body for direct POST /tasks,
//            but injected from URL params in nested routes — exclude it from taskCreateNestedSchema
// BUSINESS RULE: title must be non-empty and trimmed
// BUSINESS RULE: status must be one of: todo, in_progress, done
// BUSINESS RULE: priority must be an integer from 1 (lowest) to 5 (highest)
// BUSINESS RULE: assigneeId is optional; when provided it must reference an existing User
// FIELD DEFAULT: status has @default("todo") — MUST be .optional() in createSchema
// FIELD DEFAULT: priority has @default(1) — MUST be .optional() in createSchema
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
// FIELD DEFAULT: updatedAt has @default(now()) — MUST be .optional() in createSchema
const taskCreateSchema = z.object({});
const taskCreateNestedSchema = z.object({});
const taskUpdateSchema = z.object({});
/* LLM_SECTION_END */

function formatErrors(errors: z.ZodIssue[]): string {
  const seen = new Set<string>();
  return errors
    .map(e => {
      const field = e.path.length > 0 ? e.path.join('.') : null;
      return field ? `${field}: ${e.message}` : e.message;
    })
    .filter(msg => {
      if (seen.has(msg)) return false;
      seen.add(msg);
      return true;
    })
    .join(', ');
}

export function validateTaskCreate(body: unknown): TaskCreateInput {
  const result = taskCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as TaskCreateInput;
}

export function validateTaskCreateNested(body: unknown): TaskCreateInput {
  const result = taskCreateNestedSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as TaskCreateInput;
}

export function validateTaskUpdate(body: unknown): TaskUpdateInput {
  const result = taskUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as TaskUpdateInput;
}
