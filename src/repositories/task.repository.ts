import { prisma } from '../lib/prisma.js';
import { ListQueryParams } from '../lib/pagination.js';
import { TaskCreateInput, TaskUpdateInput } from '../types/task.types.js';


export class TaskRepository {
  async findMany(
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = {};
    if (params.filters['title'] !== undefined) {
      where['title'] = params.filters['title'];
    }
    if (params.filters['description'] !== undefined) {
      where['description'] = params.filters['description'];
    }
    if (params.filters['status'] !== undefined) {
      where['status'] = params.filters['status'];
    }
    if (params.filters['priority'] !== undefined) {
      const _v4 = Number(params.filters['priority']);
      if (!isNaN(_v4)) where['priority'] = _v4;
    }
    if (params.filters['projectId'] !== undefined) {
      const _v5 = Number(params.filters['projectId']);
      if (!isNaN(_v5)) where['projectId'] = _v5;
    }
    if (params.filters['assigneeId'] !== undefined) {
      const _v6 = Number(params.filters['assigneeId']);
      if (!isNaN(_v6)) where['assigneeId'] = _v6;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.task.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.task.count({ where }),
    ]);

    return { data, total };
  }

  async findById(id: number): Promise<any | null> {
    return prisma.task.findUnique({
      where: { id: id },
    });
  }

  async create(data: TaskCreateInput): Promise<any> {
    return prisma.task.create({
      // Cast to any: custom type name clashes with Prisma's checked variant; scalar FKs resolve correctly at runtime.
      data: data as any,
    });
  }

  async update(id: number, data: TaskUpdateInput): Promise<any | null> {
    try {
      return await prisma.task.update({
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
      // Delete child records first to avoid FK constraint violations, then delete this entity.
      await prisma.$transaction([
        prisma.taskComment.deleteMany({ where: { taskId: id } }),
        prisma.task.delete({ where: { id: id } }),
      ]);
      return true;
    } catch (err: any) {
      if (err.code === 'P2025') return false;
      throw err;
    }
  }
  // Find all tasks belonging to a parent via projectId
  async findManyByProjectId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { projectId: parentId };
    if (params.filters['title'] !== undefined) {
      where['title'] = params.filters['title'];
    }
    if (params.filters['description'] !== undefined) {
      where['description'] = params.filters['description'];
    }
    if (params.filters['status'] !== undefined) {
      where['status'] = params.filters['status'];
    }
    if (params.filters['priority'] !== undefined) {
      const _v4 = Number(params.filters['priority']);
      if (!isNaN(_v4)) where['priority'] = _v4;
    }
    if (params.filters['projectId'] !== undefined) {
      const _v5 = Number(params.filters['projectId']);
      if (!isNaN(_v5)) where['projectId'] = _v5;
    }
    if (params.filters['assigneeId'] !== undefined) {
      const _v6 = Number(params.filters['assigneeId']);
      if (!isNaN(_v6)) where['assigneeId'] = _v6;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.task.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.task.count({ where }),
    ]);

    return { data, total };
  }
  // Find all tasks belonging to a parent via assigneeId
  async findManyByAssigneeId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { assigneeId: parentId };
    if (params.filters['title'] !== undefined) {
      where['title'] = params.filters['title'];
    }
    if (params.filters['description'] !== undefined) {
      where['description'] = params.filters['description'];
    }
    if (params.filters['status'] !== undefined) {
      where['status'] = params.filters['status'];
    }
    if (params.filters['priority'] !== undefined) {
      const _v4 = Number(params.filters['priority']);
      if (!isNaN(_v4)) where['priority'] = _v4;
    }
    if (params.filters['projectId'] !== undefined) {
      const _v5 = Number(params.filters['projectId']);
      if (!isNaN(_v5)) where['projectId'] = _v5;
    }
    if (params.filters['assigneeId'] !== undefined) {
      const _v6 = Number(params.filters['assigneeId']);
      if (!isNaN(_v6)) where['assigneeId'] = _v6;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.task.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.task.count({ where }),
    ]);

    return { data, total };
  }
}
