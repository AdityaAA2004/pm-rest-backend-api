import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { OrganizationCreateInput, OrganizationUpdateInput } from '../types/organization.types.js';

/* LLM_SECTION_START */
// Entity: Organization
// Fields (name: ts_type, required/optional):
//   name: string (required)
//   slug: string (required)
//   description: string (optional)
//   website: string (optional)
//   createdAt: Date (required)
//   updatedAt: Date (required)
// TODO: define Zod schemas for Organization create and update
// BUSINESS RULE: Name and slug must be unique across all organizations
// BUSINESS RULE: slug must be lowercase, alphanumeric with hyphens only
// BUSINESS RULE: website is optional and must be a valid URL when provided
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
// FIELD DEFAULT: updatedAt has @default(now()) — MUST be .optional() in createSchema
const organizationCreateSchema = z.object({});
const organizationUpdateSchema = z.object({});
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
