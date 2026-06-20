export interface MembershipCreateInput {
  role?: string;
  userId: number;
  organizationId: number;
  createdAt?: Date;
}

export type MembershipUpdateInput = Partial<MembershipCreateInput>;
