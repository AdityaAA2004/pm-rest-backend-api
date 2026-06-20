import { Router } from 'express';
import { OrganizationController } from '../controllers/organization.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new OrganizationController();

// List all organizations with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single organization by ID
router.get('/:id', controller.getById.bind(controller));
// Create a new organization (requires authentication)
router.post('/', authenticate, controller.create.bind(controller));
// Update an existing organization (requires authentication)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a organization (requires authentication)
router.delete('/:id', authenticate, controller.remove.bind(controller));

// --- Nested routes: memberships under Organization ---
// List all memberships for a organization (always available)
router.get('/:id/memberships', controller.getMembershipsForOrganization.bind(controller));
// Create a membership — canonical create route (primary parent: Organization)
router.post('/:id/memberships', authenticate, controller.createMembershipForOrganization.bind(controller));

// --- Nested routes: projects under Organization ---
// List all projects for a organization (always available)
router.get('/:id/projects', controller.getProjectsForOrganization.bind(controller));
// Create a project — canonical create route (primary parent: Organization)
router.post('/:id/projects', authenticate, controller.createProjectForOrganization.bind(controller));

export { router as organizationsRouter };
