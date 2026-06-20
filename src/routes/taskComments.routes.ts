import { Router } from 'express';
import { TaskCommentController } from '../controllers/taskComment.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new TaskCommentController();

// List all taskComments with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single taskComment by ID
router.get('/:id', controller.getById.bind(controller));
// Update an existing taskComment (requires authentication + ownership)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a taskComment (requires authentication + ownership)
router.delete('/:id', authenticate, controller.remove.bind(controller));

export { router as taskCommentsRouter };
