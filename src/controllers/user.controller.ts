import { Request, Response, NextFunction } from 'express';
import { UserRepository } from '../repositories/user.repository.js';
import { validateUserCreate, validateUserUpdate } from '../validators/user.validator.js';
import { parseListQuery, buildPaginatedResponse } from '../lib/pagination.js';
import { NotFoundError, AppError } from '../lib/errors.js';
import { MembershipRepository } from '../repositories/membership.repository.js';
import { validateMembershipCreate, validateMembershipCreateNested, validateMembershipUpdate } from '../validators/membership.validator.js';
import { TaskRepository } from '../repositories/task.repository.js';
import { validateTaskCreate, validateTaskCreateNested, validateTaskUpdate } from '../validators/task.validator.js';
import { TaskCommentRepository } from '../repositories/taskComment.repository.js';
import { validateTaskCommentCreate, validateTaskCommentCreateNested, validateTaskCommentUpdate } from '../validators/taskComment.validator.js';

export class UserController {
  private repository: UserRepository;
  private membershipRepository: MembershipRepository;
  private taskRepository: TaskRepository;
  private taskCommentRepository: TaskCommentRepository;

  constructor() {
    this.repository = new UserRepository();
    this.membershipRepository = new MembershipRepository();
    this.taskRepository = new TaskRepository();
    this.taskCommentRepository = new TaskCommentRepository();
  }

  private readonly ALLOWED_FILTER_FIELDS = ['email', 'username', 'displayName'] as const;
  private readonly ALLOWED_SORT_FIELDS = ['id', 'email', 'username', 'displayName'] as const;

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
        throw new NotFoundError('User', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async create(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = validateUserCreate(req.body);
      const record = await this.repository.create(data);
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }

  async update(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      if (id !== req.user!.id) {
        throw new AppError(403, 'Forbidden');
      }
      const data = validateUserUpdate(req.body);
      const record = await this.repository.update(id, data);
      if (!record) {
        throw new NotFoundError('User', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async remove(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      if (id !== req.user!.id) {
        throw new AppError(403, 'Forbidden');
      }
      const deleted = await this.repository.delete(id);
      if (!deleted) {
        throw new NotFoundError('User', id);
      }
      res.status(204).send();
    } catch (err) {
      next(err);
    }
  }

  // --- Nested: Membership under User ---

  async getMembershipsForUser(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      const nestedFilterFields = ['role', 'userId', 'organizationId'] as const;
      const nestedSortFields = ['id', 'role', 'userId', 'organizationId'] as const;
      const params = parseListQuery(req, nestedFilterFields, nestedSortFields);
      const { data, total } = await this.membershipRepository.findManyByUserId(parentId, params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async createMembershipForUser(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      // Parent ID comes from the authenticated user's token, not the URL
      const parentId = req.user!.id;
      const data = validateMembershipCreate(req.body);
      // Inject the parent FK; ignore any userId provided in the body
      const record = await this.membershipRepository.create({ ...data, userId: parentId });
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }


  // --- Nested: Task under User ---

  async getTasksForUser(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      const nestedFilterFields = ['title', 'description', 'status', 'priority', 'projectId', 'assigneeId'] as const;
      const nestedSortFields = ['id', 'title', 'description', 'status', 'priority', 'projectId', 'assigneeId'] as const;
      const params = parseListQuery(req, nestedFilterFields, nestedSortFields);
      const { data, total } = await this.taskRepository.findManyByAssigneeId(parentId, params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async createTaskForUser(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      // Parent ID comes from the authenticated user's token, not the URL
      const parentId = req.user!.id;
      const data = validateTaskCreate(req.body);
      // Inject the parent FK; ignore any assigneeId provided in the body
      const record = await this.taskRepository.create({ ...data, assigneeId: parentId });
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }


  // --- Nested: TaskComment under User ---

  async getTaskCommentsForUser(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      const nestedFilterFields = ['body', 'authorId', 'taskId'] as const;
      const nestedSortFields = ['id', 'body', 'authorId', 'taskId'] as const;
      const params = parseListQuery(req, nestedFilterFields, nestedSortFields);
      const { data, total } = await this.taskCommentRepository.findManyByAuthorId(parentId, params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async createTaskCommentForUser(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      // Parent ID comes from the authenticated user's token, not the URL
      const parentId = req.user!.id;
      const data = validateTaskCommentCreate(req.body);
      // Inject the parent FK; ignore any authorId provided in the body
      const record = await this.taskCommentRepository.create({ ...data, authorId: parentId });
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
