export interface ProjectCreateInput {
  name: string;
  description?: string;
  archived?: boolean;
  organizationId: number;
  createdAt?: Date;
  updatedAt?: Date;
}

export type ProjectUpdateInput = Partial<ProjectCreateInput>;
