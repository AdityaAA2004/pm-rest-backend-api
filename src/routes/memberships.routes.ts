import { Router } from 'express';
import { MembershipController } from '../controllers/membership.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new MembershipController();

// List all memberships with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single membership by ID
router.get('/:id', controller.getById.bind(controller));
// Update an existing membership (requires authentication + ownership)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a membership (requires authentication + ownership)
router.delete('/:id', authenticate, controller.remove.bind(controller));

export { router as membershipsRouter };
