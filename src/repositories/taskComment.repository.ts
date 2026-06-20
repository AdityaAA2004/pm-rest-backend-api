import { prisma } from '../lib/prisma.js';
import { ListQueryParams } from '../lib/pagination.js';
import { TaskCommentCreateInput, TaskCommentUpdateInput } from '../types/taskComment.types.js';


export class TaskCommentRepository {
  async findMany(
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = {};
    if (params.filters['body'] !== undefined) {
      where['body'] = params.filters['body'];
    }
    if (params.filters['authorId'] !== undefined) {
      const _v2 = Number(params.filters['authorId']);
      if (!isNaN(_v2)) where['authorId'] = _v2;
    }
    if (params.filters['taskId'] !== undefined) {
      const _v3 = Number(params.filters['taskId']);
      if (!isNaN(_v3)) where['taskId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.taskComment.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.taskComment.count({ where }),
    ]);

    return { data, total };
  }

  async findById(id: number): Promise<any | null> {
    return prisma.taskComment.findUnique({
      where: { id: id },
    });
  }

  async create(data: TaskCommentCreateInput): Promise<any> {
    return prisma.taskComment.create({
      // Cast to any: custom type name clashes with Prisma's checked variant; scalar FKs resolve correctly at runtime.
      data: data as any,
    });
  }

  async update(id: number, data: TaskCommentUpdateInput): Promise<any | null> {
    try {
      return await prisma.taskComment.update({
        where: { id: id },
        // Cast to any: see create() comment above.
        data: data as any,
      });
    } catch (err: any) {
      if (err.code === 'P2025') return null;
      throw err;
    }
  }

  async delete(id: number): Promise<boolean> {
    try {
      await prisma.taskComment.delete({
        where: { id: id },
      });
      return true;
    } catch (err: any) {
      if (err.code === 'P2025') return false;
      throw err;
    }
  }
  // Find all taskComments belonging to a parent via authorId
  async findManyByAuthorId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { authorId: parentId };
    if (params.filters['body'] !== undefined) {
      where['body'] = params.filters['body'];
    }
    if (params.filters['authorId'] !== undefined) {
      const _v2 = Number(params.filters['authorId']);
      if (!isNaN(_v2)) where['authorId'] = _v2;
    }
    if (params.filters['taskId'] !== undefined) {
      const _v3 = Number(params.filters['taskId']);
      if (!isNaN(_v3)) where['taskId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.taskComment.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.taskComment.count({ where }),
    ]);

    return { data, total };
  }
  // Find all taskComments belonging to a parent via taskId
  async findManyByTaskId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { taskId: parentId };
    if (params.filters['body'] !== undefined) {
      where['body'] = params.filters['body'];
    }
    if (params.filters['authorId'] !== undefined) {
      const _v2 = Number(params.filters['authorId']);
      if (!isNaN(_v2)) where['authorId'] = _v2;
    }
    if (params.filters['taskId'] !== undefined) {
      const _v3 = Number(params.filters['taskId']);
      if (!isNaN(_v3)) where['taskId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.taskComment.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.taskComment.count({ where }),
    ]);

    return { data, total };
  }
}
