export interface UserCreateInput {
  email: string;
  username: string;
  password: string;
  displayName?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export type UserUpdateInput = Partial<UserCreateInput>;
