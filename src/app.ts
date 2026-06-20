import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { usersRouter } from './routes/users.routes.js';
import { organizationsRouter } from './routes/organizations.routes.js';
import { membershipsRouter } from './routes/memberships.routes.js';
import { projectsRouter } from './routes/projects.routes.js';
import { tasksRouter } from './routes/tasks.routes.js';
import { taskCommentsRouter } from './routes/taskComments.routes.js';
import { authRouter } from './routes/auth.routes.js';
import { errorHandler } from './lib/errors.js';

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

app.use('/auth', authRouter);
app.use('/api/users', usersRouter);
app.use('/api/organizations', organizationsRouter);
app.use('/api/memberships', membershipsRouter);
app.use('/api/projects', projectsRouter);
app.use('/api/tasks', tasksRouter);
app.use('/api/taskComments', taskCommentsRouter);

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.use((_req, res) => {
  res.status(404).json({ error: 'Not found' });
});

app.use(errorHandler);

export default app;
