import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { MembershipCreateInput, MembershipUpdateInput } from '../types/membership.types.js';

const membershipCreateSchema = z.object({
  organizationId: z.number(),
  role: z.enum(['owner', 'admin', 'member']).optional(),
  createdAt: z.coerce.date().optional(),
});
const membershipCreateNestedSchema = z.object({
  role: z.enum(['owner', 'admin', 'member']).optional(),
  createdAt: z.coerce.date().optional(),
});
const membershipUpdateSchema = membershipCreateSchema.partial();

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
