import { Router } from 'express';
import { UserController } from '../controllers/user.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new UserController();

// List all users with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single user by ID
router.get('/:id', controller.getById.bind(controller));
// Create a new user (requires authentication)
router.post('/', authenticate, controller.create.bind(controller));
// Update an existing user (requires authentication)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a user (requires authentication)
router.delete('/:id', authenticate, controller.remove.bind(controller));

// --- Nested routes: memberships under User ---
// List all memberships for a user (always available)
router.get('/:id/memberships', controller.getMembershipsForUser.bind(controller));

// --- Nested routes: tasks under User ---
// List all tasks for a user (always available)
router.get('/:id/tasks', controller.getTasksForUser.bind(controller));

// --- Nested routes: taskComments under User ---
// List all taskComments for a user (always available)
router.get('/:id/comments', controller.getTaskCommentsForUser.bind(controller));

export { router as usersRouter };
