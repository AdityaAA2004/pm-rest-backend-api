import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { ProjectCreateInput, ProjectUpdateInput } from '../types/project.types.js';

/* LLM_SECTION_START */
// Entity: Project
// Fields (name: ts_type, required/optional):
//   name: string (required)
//   description: string (optional)
//   archived: boolean (required)
//   organizationId: number (required)
//   createdAt: Date (required)
//   updatedAt: Date (required)
// TODO: define Zod schemas for Project create and update
// PARENT-FK: organizationId is required in the request body for direct POST /projects,
//            but injected from URL params in nested routes — exclude it from projectCreateNestedSchema
// BUSINESS RULE: name must be non-empty and trimmed
// BUSINESS RULE: description is optional free text
// BUSINESS RULE: archived defaults to false; can be updated to archive a project
// FIELD DEFAULT: archived has @default(false) — MUST be .optional() in createSchema
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
// FIELD DEFAULT: updatedAt has @default(now()) — MUST be .optional() in createSchema
const projectCreateSchema = z.object({});
const projectCreateNestedSchema = z.object({});
const projectUpdateSchema = z.object({});
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
