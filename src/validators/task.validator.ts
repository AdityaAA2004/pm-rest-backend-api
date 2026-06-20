import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { TaskCreateInput, TaskUpdateInput } from '../types/task.types.js';

const taskCreateSchema = z.object({
  projectId: z.number(),
  title: z.string().min(1).max(255).trim(),
  description: z.string().min(1).max(10000).optional(),
  status: z.enum(['todo', 'in_progress', 'done']).optional(),
  priority: z.number().int().min(1).max(5).optional(),
  assigneeId: z.number().optional(),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const taskCreateNestedSchema = z.object({
  title: z.string().min(1).max(255).trim(),
  description: z.string().min(1).max(10000).optional(),
  status: z.enum(['todo', 'in_progress', 'done']).optional(),
  priority: z.number().int().min(1).max(5).optional(),
  assigneeId: z.number().optional(),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const taskUpdateSchema = taskCreateSchema.partial();

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
