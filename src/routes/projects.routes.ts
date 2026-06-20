import { Router } from 'express';
import { ProjectController } from '../controllers/project.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new ProjectController();

// List all projects with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single project by ID
router.get('/:id', controller.getById.bind(controller));
// Update an existing project (requires authentication)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a project (requires authentication)
router.delete('/:id', authenticate, controller.remove.bind(controller));

// --- Nested routes: tasks under Project ---
// List all tasks for a project (always available)
router.get('/:id/tasks', controller.getTasksForProject.bind(controller));
// Create a task — canonical create route (primary parent: Project)
router.post('/:id/tasks', authenticate, controller.createTaskForProject.bind(controller));

export { router as projectsRouter };
