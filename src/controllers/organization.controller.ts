import { Request, Response, NextFunction } from 'express';
import { OrganizationRepository } from '../repositories/organization.repository.js';
import { validateOrganizationCreate, validateOrganizationUpdate } from '../validators/organization.validator.js';
import { parseListQuery, buildPaginatedResponse } from '../lib/pagination.js';
import { NotFoundError, AppError } from '../lib/errors.js';
import { MembershipRepository } from '../repositories/membership.repository.js';
import { validateMembershipCreate, validateMembershipCreateNested, validateMembershipUpdate } from '../validators/membership.validator.js';
import { ProjectRepository } from '../repositories/project.repository.js';
import { validateProjectCreate, validateProjectCreateNested, validateProjectUpdate } from '../validators/project.validator.js';

export class OrganizationController {
  private repository: OrganizationRepository;
  private membershipRepository: MembershipRepository;
  private projectRepository: ProjectRepository;

  constructor() {
    this.repository = new OrganizationRepository();
    this.membershipRepository = new MembershipRepository();
    this.projectRepository = new ProjectRepository();
  }

  private readonly ALLOWED_FILTER_FIELDS = ['name', 'slug', 'description', 'website'] as const;
  private readonly ALLOWED_SORT_FIELDS = ['id', 'name', 'slug', 'description', 'website'] as const;

  async getAll(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const params = parseListQuery(req, this.ALLOWED_FILTER_FIELDS, this.ALLOWED_SORT_FIELDS);
      const { data, total } = await this.repository.findMany(params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async getById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      const record = await this.repository.findById(id);
      if (!record) {
        throw new NotFoundError('Organization', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async create(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = validateOrganizationCreate(req.body);
      const record = await this.repository.create(data);
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }

  async update(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      const data = validateOrganizationUpdate(req.body);
      const record = await this.repository.update(id, data);
      if (!record) {
        throw new NotFoundError('Organization', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async remove(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      const deleted = await this.repository.delete(id);
      if (!deleted) {
        throw new NotFoundError('Organization', id);
      }
      res.status(204).send();
    } catch (err) {
      next(err);
    }
  }

  // --- Nested: Membership under Organization ---

  async getMembershipsForOrganization(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      const nestedFilterFields = ['role', 'userId', 'organizationId'] as const;
      const nestedSortFields = ['id', 'role', 'userId', 'organizationId'] as const;
      const params = parseListQuery(req, nestedFilterFields, nestedSortFields);
      const { data, total } = await this.membershipRepository.findManyByOrganizationId(parentId, params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async createMembershipForOrganization(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      // Use the nested schema: parent FK (organizationId) is injected from URL, not expected in body
      const data = validateMembershipCreateNested(req.body);
      // Inject the parent FK; ignore any organizationId provided in the body
      // Also inject the owner FK (userId) from the authenticated user's token
      const record = await this.membershipRepository.create({ ...data, organizationId: parentId, userId: req.user!.id });
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }


  // --- Nested: Project under Organization ---

  async getProjectsForOrganization(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      const nestedFilterFields = ['name', 'description', 'archived', 'organizationId'] as const;
      const nestedSortFields = ['id', 'name', 'description', 'archived', 'organizationId'] as const;
      const params = parseListQuery(req, nestedFilterFields, nestedSortFields);
      const { data, total } = await this.projectRepository.findManyByOrganizationId(parentId, params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async createProjectForOrganization(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      // Use the nested schema: parent FK (organizationId) is injected from URL, not expected in body
      const data = validateProjectCreateNested(req.body);
      // Inject the parent FK; ignore any organizationId provided in the body
      const record = await this.projectRepository.create({ ...data, organizationId: parentId });
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }


  private _parseId(raw: string): number {
    if (!/^\d+$/.test(raw)) {
      throw new AppError(400, 'Invalid ID format');
    }
    const id = Number(raw);
    if (id > Number.MAX_SAFE_INTEGER) {
      throw new AppError(400, 'ID out of range');
    }
    return id;
  }
}
