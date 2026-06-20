import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { MembershipCreateInput, MembershipUpdateInput } from '../types/membership.types.js';

/* LLM_SECTION_START */
// Entity: Membership
// Fields (name: ts_type, required/optional):
//   role: string (required)
//   userId: number (required)
//   organizationId: number (required)
//   createdAt: Date (required)
// TODO: define Zod schemas for Membership create and update
// SERVER-INJECTED (always): userId is set from req.user.id — exclude from ALL schemas
// PARENT-FK: organizationId is required in the request body for direct POST /memberships,
//            but injected from URL params in nested routes — exclude it from membershipCreateNestedSchema
// BUSINESS RULE: role must be one of: owner, admin, member
// BUSINESS RULE: A user can only have one membership per organization
// FIELD DEFAULT: role has @default("member") — MUST be .optional() in createSchema
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
const membershipCreateSchema = z.object({});
const membershipCreateNestedSchema = z.object({});
const membershipUpdateSchema = z.object({});
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

export function validateMembershipCreate(body: unknown): MembershipCreateInput {
  const result = membershipCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as MembershipCreateInput;
}

export function validateMembershipCreateNested(body: unknown): MembershipCreateInput {
  const result = membershipCreateNestedSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as MembershipCreateInput;
}

export function validateMembershipUpdate(body: unknown): MembershipUpdateInput {
  const result = membershipUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as MembershipUpdateInput;
}
