import { Router } from 'express';
import { TaskController } from '../controllers/task.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new TaskController();

// List all tasks with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single task by ID
router.get('/:id', controller.getById.bind(controller));
// Update an existing task (requires authentication)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a task (requires authentication)
router.delete('/:id', authenticate, controller.remove.bind(controller));

// --- Nested routes: taskComments under Task ---
// List all taskComments for a task (always available)
router.get('/:id/comments', controller.getTaskCommentsForTask.bind(controller));
// Create a taskComment — canonical create route (primary parent: Task)
router.post('/:id/comments', authenticate, controller.createTaskCommentForTask.bind(controller));

export { router as tasksRouter };
