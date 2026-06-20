import { Request, Response, NextFunction } from 'express';
import { TaskRepository } from '../repositories/task.repository.js';
import { validateTaskCreate, validateTaskUpdate } from '../validators/task.validator.js';
import { parseListQuery, buildPaginatedResponse } from '../lib/pagination.js';
import { NotFoundError, AppError } from '../lib/errors.js';
import { TaskCommentRepository } from '../repositories/taskComment.repository.js';
import { validateTaskCommentCreate, validateTaskCommentCreateNested, validateTaskCommentUpdate } from '../validators/taskComment.validator.js';

export class TaskController {
  private repository: TaskRepository;
  private taskCommentRepository: TaskCommentRepository;

  constructor() {
    this.repository = new TaskRepository();
    this.taskCommentRepository = new TaskCommentRepository();
  }

  private readonly ALLOWED_FILTER_FIELDS = ['title', 'description', 'status', 'priority', 'projectId', 'assigneeId'] as const;
  private readonly ALLOWED_SORT_FIELDS = ['id', 'title', 'description', 'status', 'priority', 'projectId', 'assigneeId'] as const;

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
        throw new NotFoundError('Task', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async create(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = validateTaskCreate(req.body);
      const record = await this.repository.create(data);
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }

  async update(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      const data = validateTaskUpdate(req.body);
      const record = await this.repository.update(id, data);
      if (!record) {
        throw new NotFoundError('Task', id);
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
        throw new NotFoundError('Task', id);
      }
      res.status(204).send();
    } catch (err) {
      next(err);
    }
  }

  // --- Nested: TaskComment under Task ---

  async getTaskCommentsForTask(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      const nestedFilterFields = ['body', 'authorId', 'taskId'] as const;
      const nestedSortFields = ['id', 'body', 'authorId', 'taskId'] as const;
      const params = parseListQuery(req, nestedFilterFields, nestedSortFields);
      const { data, total } = await this.taskCommentRepository.findManyByTaskId(parentId, params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async createTaskCommentForTask(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      // Use the nested schema: parent FK (taskId) is injected from URL, not expected in body
      const data = validateTaskCommentCreateNested(req.body);
      // Inject the parent FK; ignore any taskId provided in the body
      // Also inject the owner FK (authorId) from the authenticated user's token
      const record = await this.taskCommentRepository.create({ ...data, taskId: parentId, authorId: req.user!.id });
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
