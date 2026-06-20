import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { TaskCommentCreateInput, TaskCommentUpdateInput } from '../types/taskComment.types.js';

/* LLM_SECTION_START */
// Entity: TaskComment
// Fields (name: ts_type, required/optional):
//   body: string (required)
//   authorId: number (required)
//   taskId: number (required)
//   createdAt: Date (required)
//   updatedAt: Date (required)
// TODO: define Zod schemas for TaskComment create and update
// SERVER-INJECTED (always): authorId is set from req.user.id — exclude from ALL schemas
// PARENT-FK: taskId is required in the request body for direct POST /taskComments,
//            but injected from URL params in nested routes — exclude it from taskCommentCreateNestedSchema
// BUSINESS RULE: body must be non-empty
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
// FIELD DEFAULT: updatedAt has @default(now()) — MUST be .optional() in createSchema
const taskCommentCreateSchema = z.object({});
const taskCommentCreateNestedSchema = z.object({});
const taskCommentUpdateSchema = z.object({});
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

export function validateTaskCommentCreate(body: unknown): TaskCommentCreateInput {
  const result = taskCommentCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as TaskCommentCreateInput;
}

export function validateTaskCommentCreateNested(body: unknown): TaskCommentCreateInput {
  const result = taskCommentCreateNestedSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as TaskCommentCreateInput;
}

export function validateTaskCommentUpdate(body: unknown): TaskCommentUpdateInput {
  const result = taskCommentUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as TaskCommentUpdateInput;
}
