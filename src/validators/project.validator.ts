import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { ProjectCreateInput, ProjectUpdateInput } from '../types/project.types.js';

const projectCreateSchema = z.object({
  organizationId: z.number(),
  name: z.string().min(1).max(255).trim(),
  description: z.string().min(1).max(10000).optional(),
  archived: z.boolean().optional(),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const projectCreateNestedSchema = z.object({
  name: z.string().min(1).max(255).trim(),
  description: z.string().min(1).max(10000).optional(),
  archived: z.boolean().optional(),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const projectUpdateSchema = projectCreateSchema.partial();

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

export function validateProjectCreate(body: unknown): ProjectCreateInput {
  const result = projectCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as ProjectCreateInput;
}

export function validateProjectCreateNested(body: unknown): ProjectCreateInput {
  const result = projectCreateNestedSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as ProjectCreateInput;
}

export function validateProjectUpdate(body: unknown): ProjectUpdateInput {
  const result = projectUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as ProjectUpdateInput;
}
