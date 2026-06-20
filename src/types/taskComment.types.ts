export interface TaskCommentCreateInput {
  body: string;
  authorId: number;
  taskId: number;
  createdAt?: Date;
  updatedAt?: Date;
}

export type TaskCommentUpdateInput = Partial<TaskCommentCreateInput>;
