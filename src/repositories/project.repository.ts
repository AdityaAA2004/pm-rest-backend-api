import { prisma } from '../lib/prisma.js';
import { ListQueryParams } from '../lib/pagination.js';
import { ProjectCreateInput, ProjectUpdateInput } from '../types/project.types.js';


export class ProjectRepository {
  async findMany(
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = {};
    if (params.filters['name'] !== undefined) {
      where['name'] = params.filters['name'];
    }
    if (params.filters['description'] !== undefined) {
      where['description'] = params.filters['description'];
    }
    if (params.filters['archived'] !== undefined) {
      where['archived'] = params.filters['archived'] === 'true';
    }
    if (params.filters['organizationId'] !== undefined) {
      const _v4 = Number(params.filters['organizationId']);
      if (!isNaN(_v4)) where['organizationId'] = _v4;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.project.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.project.count({ where }),
    ]);

    return { data, total };
  }

  async findById(id: number): Promise<any | null> {
    return prisma.project.findUnique({
      where: { id: id },
    });
  }

  async create(data: ProjectCreateInput): Promise<any> {
    return prisma.project.create({
      // Cast to any: custom type name clashes with Prisma's checked variant; scalar FKs resolve correctly at runtime.
      data: data as any,
    });
  }

  async update(id: number, data: ProjectUpdateInput): Promise<any | null> {
    try {
      return await prisma.project.update({
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
        prisma.task.deleteMany({ where: { projectId: id } }),
        prisma.project.delete({ where: { id: id } }),
      ]);
      return true;
    } catch (err: any) {
      if (err.code === 'P2025') return false;
      throw err;
    }
  }
  // Find all projects belonging to a parent via organizationId
  async findManyByOrganizationId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { organizationId: parentId };
    if (params.filters['name'] !== undefined) {
      where['name'] = params.filters['name'];
    }
    if (params.filters['description'] !== undefined) {
      where['description'] = params.filters['description'];
    }
    if (params.filters['archived'] !== undefined) {
      where['archived'] = params.filters['archived'] === 'true';
    }
    if (params.filters['organizationId'] !== undefined) {
      const _v4 = Number(params.filters['organizationId']);
      if (!isNaN(_v4)) where['organizationId'] = _v4;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.project.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.project.count({ where }),
    ]);

    return { data, total };
  }
}
