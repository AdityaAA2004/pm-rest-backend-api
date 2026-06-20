import { Request, Response, NextFunction } from 'express';
import { ProjectRepository } from '../repositories/project.repository.js';
import { validateProjectCreate, validateProjectUpdate } from '../validators/project.validator.js';
import { parseListQuery, buildPaginatedResponse } from '../lib/pagination.js';
import { NotFoundError, AppError } from '../lib/errors.js';
import { TaskRepository } from '../repositories/task.repository.js';
import { validateTaskCreate, validateTaskCreateNested, validateTaskUpdate } from '../validators/task.validator.js';

export class ProjectController {
  private repository: ProjectRepository;
  private taskRepository: TaskRepository;

  constructor() {
    this.repository = new ProjectRepository();
    this.taskRepository = new TaskRepository();
  }

  private readonly ALLOWED_FILTER_FIELDS = ['name', 'description', 'archived', 'organizationId'] as const;
  private readonly ALLOWED_SORT_FIELDS = ['id', 'name', 'description', 'archived', 'organizationId'] as const;

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
        throw new NotFoundError('Project', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async create(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = validateProjectCreate(req.body);
      const record = await this.repository.create(data);
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }

  async update(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      const data = validateProjectUpdate(req.body);
      const record = await this.repository.update(id, data);
      if (!record) {
        throw new NotFoundError('Project', id);
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
        throw new NotFoundError('Project', id);
      }
      res.status(204).send();
    } catch (err) {
      next(err);
    }
  }

  // --- Nested: Task under Project ---

  async getTasksForProject(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      const nestedFilterFields = ['title', 'description', 'status', 'priority', 'projectId', 'assigneeId'] as const;
      const nestedSortFields = ['id', 'title', 'description', 'status', 'priority', 'projectId', 'assigneeId'] as const;
      const params = parseListQuery(req, nestedFilterFields, nestedSortFields);
      const { data, total } = await this.taskRepository.findManyByProjectId(parentId, params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async createTaskForProject(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      // Use the nested schema: parent FK (projectId) is injected from URL, not expected in body
      const data = validateTaskCreateNested(req.body);
      // Inject the parent FK; ignore any projectId provided in the body
      const record = await this.taskRepository.create({ ...data, projectId: parentId });
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
