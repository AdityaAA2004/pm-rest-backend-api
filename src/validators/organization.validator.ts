import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { OrganizationCreateInput, OrganizationUpdateInput } from '../types/organization.types.js';

const organizationCreateSchema = z.object({
  name: z.string().min(1).max(255).trim(),
  slug: z.string().min(1).max(255).trim().regex(/^[a-z0-9-]+$/, { message: 'Slug must be lowercase alphanumeric with hyphens only' }),
  description: z.string().min(1).max(10000).optional(),
  website: z.string().url().optional(),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const organizationUpdateSchema = organizationCreateSchema.partial();

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

export function validateOrganizationCreate(body: unknown): OrganizationCreateInput {
  const result = organizationCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as OrganizationCreateInput;
}

export function validateOrganizationUpdate(body: unknown): OrganizationUpdateInput {
  const result = organizationUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as OrganizationUpdateInput;
}
