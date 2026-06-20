export interface TaskCreateInput {
  title: string;
  description?: string;
  status?: string;
  priority?: number;
  projectId: number;
  assigneeId?: number;
  createdAt?: Date;
  updatedAt?: Date;
}

export type TaskUpdateInput = Partial<TaskCreateInput>;
