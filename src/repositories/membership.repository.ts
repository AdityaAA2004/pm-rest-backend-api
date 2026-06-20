import { prisma } from '../lib/prisma.js';
import { ListQueryParams } from '../lib/pagination.js';
import { MembershipCreateInput, MembershipUpdateInput } from '../types/membership.types.js';


export class MembershipRepository {
  async findMany(
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = {};
    if (params.filters['role'] !== undefined) {
      where['role'] = params.filters['role'];
    }
    if (params.filters['userId'] !== undefined) {
      const _v2 = Number(params.filters['userId']);
      if (!isNaN(_v2)) where['userId'] = _v2;
    }
    if (params.filters['organizationId'] !== undefined) {
      const _v3 = Number(params.filters['organizationId']);
      if (!isNaN(_v3)) where['organizationId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.membership.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.membership.count({ where }),
    ]);

    return { data, total };
  }

  async findById(id: number): Promise<any | null> {
    return prisma.membership.findUnique({
      where: { id: id },
    });
  }

  async create(data: MembershipCreateInput): Promise<any> {
    return prisma.membership.create({
      // Cast to any: custom type name clashes with Prisma's checked variant; scalar FKs resolve correctly at runtime.
      data: data as any,
    });
  }

  async update(id: number, data: MembershipUpdateInput): Promise<any | null> {
    try {
      return await prisma.membership.update({
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
      await prisma.membership.delete({
        where: { id: id },
      });
      return true;
    } catch (err: any) {
      if (err.code === 'P2025') return false;
      throw err;
    }
  }
  // Find all memberships belonging to a parent via userId
  async findManyByUserId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { userId: parentId };
    if (params.filters['role'] !== undefined) {
      where['role'] = params.filters['role'];
    }
    if (params.filters['userId'] !== undefined) {
      const _v2 = Number(params.filters['userId']);
      if (!isNaN(_v2)) where['userId'] = _v2;
    }
    if (params.filters['organizationId'] !== undefined) {
      const _v3 = Number(params.filters['organizationId']);
      if (!isNaN(_v3)) where['organizationId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.membership.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.membership.count({ where }),
    ]);

    return { data, total };
  }
  // Find all memberships belonging to a parent via organizationId
  async findManyByOrganizationId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { organizationId: parentId };
    if (params.filters['role'] !== undefined) {
      where['role'] = params.filters['role'];
    }
    if (params.filters['userId'] !== undefined) {
      const _v2 = Number(params.filters['userId']);
      if (!isNaN(_v2)) where['userId'] = _v2;
    }
    if (params.filters['organizationId'] !== undefined) {
      const _v3 = Number(params.filters['organizationId']);
      if (!isNaN(_v3)) where['organizationId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.membership.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.membership.count({ where }),
    ]);

    return { data, total };
  }
}
