export interface OrganizationCreateInput {
  name: string;
  slug: string;
  description?: string;
  website?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export type OrganizationUpdateInput = Partial<OrganizationCreateInput>;
