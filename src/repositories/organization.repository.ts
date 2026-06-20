import { prisma } from '../lib/prisma.js';
import { ListQueryParams } from '../lib/pagination.js';
import { OrganizationCreateInput, OrganizationUpdateInput } from '../types/organization.types.js';


export class OrganizationRepository {
  async findMany(
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = {};
    if (params.filters['name'] !== undefined) {
      where['name'] = params.filters['name'];
    }
    if (params.filters['slug'] !== undefined) {
      where['slug'] = params.filters['slug'];
    }
    if (params.filters['description'] !== undefined) {
      where['description'] = params.filters['description'];
    }
    if (params.filters['website'] !== undefined) {
      where['website'] = params.filters['website'];
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.organization.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.organization.count({ where }),
    ]);

    return { data, total };
  }

  async findById(id: number): Promise<any | null> {
    return prisma.organization.findUnique({
      where: { id: id },
    });
  }

  async create(data: OrganizationCreateInput): Promise<any> {
    return prisma.organization.create({
      // Cast to any: custom type name clashes with Prisma's checked variant; scalar FKs resolve correctly at runtime.
      data: data as any,
    });
  }

  async update(id: number, data: OrganizationUpdateInput): Promise<any | null> {
    try {
      return await prisma.organization.update({
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
        prisma.membership.deleteMany({ where: { organizationId: id } }),
        prisma.project.deleteMany({ where: { organizationId: id } }),
        prisma.organization.delete({ where: { id: id } }),
      ]);
      return true;
    } catch (err: any) {
      if (err.code === 'P2025') return false;
      throw err;
    }
  }
}
