import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { TaskCommentCreateInput, TaskCommentUpdateInput } from '../types/taskComment.types.js';

const taskCommentCreateSchema = z.object({
  taskId: z.number(),
  body: z.string().min(1).max(10000),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const taskCommentCreateNestedSchema = z.object({
  body: z.string().min(1).max(10000),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const taskCommentUpdateSchema = taskCommentCreateSchema.partial();

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
