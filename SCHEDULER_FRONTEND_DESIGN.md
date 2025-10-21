# Scheduler Module - Frontend UI Design

**Project:** YFinance Stock Analyzer UI  
**Feature:** Job Scheduler Management Interface  
**Design Date:** October 21, 2025  
**Status:** Design Phase  

---

## 1. Executive Summary

Design a new frontend page to allow users to create, manage, and monitor scheduled jobs for automatic stock data fetching. The page will integrate with the new `/scheduler` API endpoints on the backend.

### Key Features:
- ✅ Create scheduled jobs with multiple stocks
- ✅ View all scheduled jobs in a table
- ✅ Edit existing jobs
- ✅ Start/stop jobs
- ✅ Delete jobs
- ✅ Monitor scheduler status
- ✅ View job execution history

---

## 2. Technology Stack

Based on existing frontend structure:

- **Framework:** React 18.2.0
- **Router:** React Router DOM 6.16.0
- **UI Library:** Material-UI (MUI) 5.15.2
- **HTTP Client:** Axios 1.5.1
- **Icons:** FontAwesome + MUI Icons
- **Styling:** CSS Modules + Emotion
- **Date Handling:** date-fns 2.30.0

---

## 3. File Structure

```
src/
├── pages/
│   └── JobSchedulerPage.js              ← NEW (Main page component)
│
├── components/
│   ├── scheduler/                        ← NEW FOLDER
│   │   ├── JobCreationDialog.js          ← NEW (Create job modal)
│   │   ├── JobEditDialog.js              ← NEW (Edit job modal)
│   │   ├── JobsTable.js                  ← NEW (Jobs list table)
│   │   ├── SchedulerStatusCard.js        ← NEW (Status display)
│   │   └── JobExecutionHistory.js        ← NEW (Execution history)
│   │
│   └── basic/
│       └── Sidebar.js                    (UPDATE - add new menu item)
│
├── services/
│   └── api.js                            (UPDATE - add scheduler APIs)
│
├── styles/
│   └── JobSchedulerPage.css              ← NEW (Page styles)
│
└── App.js                                (UPDATE - add route)
```

---

## 4. API Integration

### 4.1 Add to `src/services/api.js`

```javascript
/** Job Scheduler API functions **/

// Create a new scheduled job
export const createScheduledJob = async (payload) => {
  return sendRequestStockData('post', '/scheduler/jobs', payload);
};

// Get all scheduled jobs
export const getScheduledJobs = async (activeOnly = false) => {
  return sendRequestStockData('get', '/scheduler/jobs', {}, { active_only: activeOnly });
};

// Get specific job details
export const getScheduledJob = async (jobId) => {
  return sendRequestStockData('get', `/scheduler/jobs/${jobId}`);
};

// Update a scheduled job
export const updateScheduledJob = async (jobId, payload) => {
  return sendRequestStockData('put', `/scheduler/jobs/${jobId}`, payload);
};

// Delete a scheduled job
export const deleteScheduledJob = async (jobId) => {
  return sendRequestStockData('delete', `/scheduler/jobs/${jobId}`);
};

// Start (activate) a job
export const startScheduledJob = async (jobId) => {
  return sendRequestStockData('post', `/scheduler/jobs/${jobId}/start`);
};

// Stop (deactivate) a job
export const stopScheduledJob = async (jobId) => {
  return sendRequestStockData('post', `/scheduler/jobs/${jobId}/stop`);
};

// Get scheduler status
export const getSchedulerStatus = async () => {
  return sendRequestStockData('get', '/scheduler/status');
};
```

---

## 5. Component Designs

### 5.1 Main Page Component: `JobSchedulerPage.js`

```javascript
// src/pages/JobSchedulerPage.js

import React, { useState, useEffect } from 'react';
import BasePage from './BasePage';
import {
  Container,
  Grid,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';

import JobCreationDialog from '../components/scheduler/JobCreationDialog';
import JobEditDialog from '../components/scheduler/JobEditDialog';
import JobsTable from '../components/scheduler/JobsTable';
import SchedulerStatusCard from '../components/scheduler/SchedulerStatusCard';

import {
  getScheduledJobs,
  getSchedulerStatus,
  deleteScheduledJob,
  startScheduledJob,
  stopScheduledJob
} from '../services/api';

import '../styles/JobSchedulerPage.css';

function JobSchedulerPage() {
  const [jobs, setJobs] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  
  // Filters
  const [showActiveOnly, setShowActiveOnly] = useState(false);

  // Load jobs and status on mount
  useEffect(() => {
    loadJobs();
    loadSchedulerStatus();
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      loadJobs();
      loadSchedulerStatus();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [showActiveOnly]);

  const loadJobs = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await getScheduledJobs(showActiveOnly);
      setJobs(data);
    } catch (err) {
      setError(`Failed to load jobs: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSchedulerStatus = async () => {
    try {
      const status = await getSchedulerStatus();
      setSchedulerStatus(status);
    } catch (err) {
      console.error('Failed to load scheduler status:', err);
    }
  };

  const handleCreateJob = () => {
    setCreateDialogOpen(true);
  };

  const handleEditJob = (job) => {
    setSelectedJob(job);
    setEditDialogOpen(true);
  };

  const handleDeleteJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job?')) {
      return;
    }
    
    try {
      await deleteScheduledJob(jobId);
      setSuccess('Job deleted successfully');
      loadJobs();
    } catch (err) {
      setError(`Failed to delete job: ${err.message}`);
    }
  };

  const handleToggleJob = async (job) => {
    try {
      if (job.is_active) {
        await stopScheduledJob(job.job_id);
        setSuccess('Job stopped successfully');
      } else {
        await startScheduledJob(job.job_id);
        setSuccess('Job started successfully');
      }
      loadJobs();
    } catch (err) {
      setError(`Failed to toggle job: ${err.message}`);
    }
  };

  const handleJobCreated = () => {
    setCreateDialogOpen(false);
    setSuccess('Job created successfully');
    loadJobs();
  };

  const handleJobUpdated = () => {
    setEditDialogOpen(false);
    setSuccess('Job updated successfully');
    loadJobs();
  };

  return (
    <BasePage>
      <Container maxWidth="xl" className="job-scheduler-page">
        <Box className="page-header">
          <Typography variant="h4" component="h1" gutterBottom>
            📅 Job Scheduler
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage scheduled jobs for automatic stock data fetching
          </Typography>
        </Box>

        {/* Status Messages */}
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Status Card */}
          <Grid item xs={12} md={4}>
            <SchedulerStatusCard status={schedulerStatus} onRefresh={loadSchedulerStatus} />
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12} md={8}>
            <Box className="quick-actions">
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={handleCreateJob}
              >
                Create New Job
              </Button>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadJobs}
                disabled={isLoading}
              >
                Refresh
              </Button>
              <Button
                variant={showActiveOnly ? 'contained' : 'outlined'}
                onClick={() => setShowActiveOnly(!showActiveOnly)}
              >
                {showActiveOnly ? 'Show All' : 'Active Only'}
              </Button>
            </Box>
          </Grid>

          {/* Jobs Table */}
          <Grid item xs={12}>
            {isLoading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <JobsTable
                jobs={jobs}
                onEdit={handleEditJob}
                onDelete={handleDeleteJob}
                onToggle={handleToggleJob}
              />
            )}
          </Grid>
        </Grid>

        {/* Dialogs */}
        <JobCreationDialog
          open={createDialogOpen}
          onClose={() => setCreateDialogOpen(false)}
          onSuccess={handleJobCreated}
        />

        <JobEditDialog
          open={editDialogOpen}
          job={selectedJob}
          onClose={() => setEditDialogOpen(false)}
          onSuccess={handleJobUpdated}
        />
      </Container>
    </BasePage>
  );
}

export default JobSchedulerPage;
```

### 5.2 Jobs Table Component: `JobsTable.js`

```javascript
// src/components/scheduler/JobsTable.js

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Box
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import { format } from 'date-fns';

function JobsTable({ jobs, onEdit, onDelete, onToggle }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'info';
      case 'failed':
        return 'error';
      case 'paused':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    try {
      return format(new Date(dateString), 'yyyy-MM-dd HH:mm');
    } catch {
      return dateString;
    }
  };

  if (jobs.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <p>No scheduled jobs found. Create your first job to get started!</p>
      </Paper>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Stocks</TableCell>
            <TableCell>Schedule</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Last Run</TableCell>
            <TableCell>Next Run</TableCell>
            <TableCell>Active</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {jobs.map((job) => (
            <TableRow key={job.job_id}>
              <TableCell>{job.name}</TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {job.stock_ids.slice(0, 3).map((stock) => (
                    <Chip key={stock} label={stock} size="small" />
                  ))}
                  {job.stock_ids.length > 3 && (
                    <Chip label={`+${job.stock_ids.length - 3}`} size="small" />
                  )}
                </Box>
              </TableCell>
              <TableCell>{job.schedule_time}</TableCell>
              <TableCell>
                <Chip
                  label={job.status}
                  color={getStatusColor(job.status)}
                  size="small"
                />
              </TableCell>
              <TableCell>{formatDate(job.last_run)}</TableCell>
              <TableCell>{formatDate(job.next_run)}</TableCell>
              <TableCell>
                <Chip
                  label={job.is_active ? 'Yes' : 'No'}
                  color={job.is_active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell align="right">
                <Tooltip title={job.is_active ? 'Stop Job' : 'Start Job'}>
                  <IconButton
                    onClick={() => onToggle(job)}
                    color={job.is_active ? 'error' : 'success'}
                    size="small"
                  >
                    {job.is_active ? <StopIcon /> : <PlayArrowIcon />}
                  </IconButton>
                </Tooltip>
                <Tooltip title="Edit Job">
                  <IconButton onClick={() => onEdit(job)} size="small">
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete Job">
                  <IconButton onClick={() => onDelete(job.job_id)} color="error" size="small">
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default JobsTable;
```

### 5.3 Job Creation Dialog: `JobCreationDialog.js`

```javascript
// src/components/scheduler/JobCreationDialog.js

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Chip,
  Alert
} from '@mui/material';
import { createScheduledJob } from '../../services/api';

function JobCreationDialog({ open, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    stock_ids: [],
    schedule_time: '17:00',
    start_date: '',
    end_date: '',
    prefix: 'scheduled_stock_data'
  });
  
  const [stockInput, setStockInput] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleAddStock = () => {
    const stock = stockInput.trim().toUpperCase();
    if (stock && !formData.stock_ids.includes(stock)) {
      setFormData({
        ...formData,
        stock_ids: [...formData.stock_ids, stock]
      });
      setStockInput('');
    }
  };

  const handleRemoveStock = (stockToRemove) => {
    setFormData({
      ...formData,
      stock_ids: formData.stock_ids.filter(stock => stock !== stockToRemove)
    });
  };

  const handleSubmit = async () => {
    // Validation
    if (!formData.name) {
      setError('Job name is required');
      return;
    }
    if (formData.stock_ids.length === 0) {
      setError('At least one stock ID is required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await createScheduledJob(formData);
      onSuccess();
      // Reset form
      setFormData({
        name: '',
        stock_ids: [],
        schedule_time: '17:00',
        start_date: '',
        end_date: '',
        prefix: 'scheduled_stock_data'
      });
    } catch (err) {
      setError(`Failed to create job: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create Scheduled Job</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            label="Job Name"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            fullWidth
            required
          />

          <Box>
            <TextField
              label="Add Stock ID"
              value={stockInput}
              onChange={(e) => setStockInput(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleAddStock()}
              placeholder="e.g., AAPL"
              fullWidth
            />
            <Button onClick={handleAddStock} sx={{ mt: 1 }}>
              Add Stock
            </Button>
            <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {formData.stock_ids.map((stock) => (
                <Chip
                  key={stock}
                  label={stock}
                  onDelete={() => handleRemoveStock(stock)}
                />
              ))}
            </Box>
          </Box>

          <TextField
            label="Schedule Time (HH:MM)"
            type="time"
            value={formData.schedule_time}
            onChange={(e) => handleInputChange('schedule_time', e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
            required
          />

          <TextField
            label="Start Date (Optional)"
            type="date"
            value={formData.start_date}
            onChange={(e) => handleInputChange('start_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
            helperText="Leave empty to fetch last 30 days"
          />

          <TextField
            label="End Date (Optional)"
            type="date"
            value={formData.end_date}
            onChange={(e) => handleInputChange('end_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
            helperText="Leave empty for today"
          />

          <TextField
            label="Data Prefix"
            value={formData.prefix}
            onChange={(e) => handleInputChange('prefix', e.target.value)}
            fullWidth
            helperText="Redis key prefix for storing data"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating...' : 'Create Job'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default JobCreationDialog;
```

### 5.4 Scheduler Status Card: `SchedulerStatusCard.js`

```javascript
// src/components/scheduler/SchedulerStatusCard.js

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

function SchedulerStatusCard({ status, onRefresh }) {
  if (!status) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6">Scheduler Status</Typography>
          <Typography color="textSecondary">Loading...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Scheduler Status</Typography>
          <Tooltip title="Refresh Status">
            <IconButton onClick={onRefresh} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Box mt={2}>
          <Box display="flex" alignItems="center" mb={2}>
            {status.is_running ? (
              <>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Chip label="Running" color="success" />
              </>
            ) : (
              <>
                <ErrorIcon color="error" sx={{ mr: 1 }} />
                <Chip label="Stopped" color="error" />
              </>
            )}
          </Box>

          <Typography variant="body2" gutterBottom>
            <strong>Total Jobs:</strong> {status.total_jobs_count}
          </Typography>
          <Typography variant="body2">
            <strong>Active Jobs:</strong> {status.active_jobs_count}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export default SchedulerStatusCard;
```

### 5.5 Job Edit Dialog: `JobEditDialog.js`

```javascript
// src/components/scheduler/JobEditDialog.js

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Chip,
  Alert,
  FormControlLabel,
  Switch
} from '@mui/material';
import { updateScheduledJob } from '../../services/api';

function JobEditDialog({ open, job, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    stock_ids: [],
    schedule_time: '17:00',
    start_date: '',
    end_date: '',
    is_active: true
  });
  
  const [stockInput, setStockInput] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (job) {
      setFormData({
        name: job.name,
        stock_ids: job.stock_ids,
        schedule_time: job.schedule_time,
        start_date: job.start_date || '',
        end_date: job.end_date || '',
        is_active: job.is_active
      });
    }
  }, [job]);

  const handleInputChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleAddStock = () => {
    const stock = stockInput.trim().toUpperCase();
    if (stock && !formData.stock_ids.includes(stock)) {
      setFormData({
        ...formData,
        stock_ids: [...formData.stock_ids, stock]
      });
      setStockInput('');
    }
  };

  const handleRemoveStock = (stockToRemove) => {
    setFormData({
      ...formData,
      stock_ids: formData.stock_ids.filter(stock => stock !== stockToRemove)
    });
  };

  const handleSubmit = async () => {
    if (!formData.name || formData.stock_ids.length === 0) {
      setError('Job name and at least one stock ID are required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await updateScheduledJob(job.job_id, formData);
      onSuccess();
    } catch (err) {
      setError(`Failed to update job: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!job) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Job: {job.name}</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            label="Job Name"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            fullWidth
            required
          />

          <Box>
            <TextField
              label="Add Stock ID"
              value={stockInput}
              onChange={(e) => setStockInput(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleAddStock()}
              placeholder="e.g., MSFT"
              fullWidth
            />
            <Button onClick={handleAddStock} sx={{ mt: 1 }}>
              Add Stock
            </Button>
            <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {formData.stock_ids.map((stock) => (
                <Chip
                  key={stock}
                  label={stock}
                  onDelete={() => handleRemoveStock(stock)}
                />
              ))}
            </Box>
          </Box>

          <TextField
            label="Schedule Time (HH:MM)"
            type="time"
            value={formData.schedule_time}
            onChange={(e) => handleInputChange('schedule_time', e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
            required
          />

          <TextField
            label="Start Date (Optional)"
            type="date"
            value={formData.start_date}
            onChange={(e) => handleInputChange('start_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
          />

          <TextField
            label="End Date (Optional)"
            type="date"
            value={formData.end_date}
            onChange={(e) => handleInputChange('end_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
          />

          <FormControlLabel
            control={
              <Switch
                checked={formData.is_active}
                onChange={(e) => handleInputChange('is_active', e.target.checked)}
              />
            }
            label="Active"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Updating...' : 'Update Job'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default JobEditDialog;
```

---

## 6. Update Existing Files

### 6.1 Update `src/App.js`

Add the new route:

```javascript
// Add import at top
import JobSchedulerPage from './pages/JobSchedulerPage';

// Add route in Routes
<Route 
  path="/job-scheduler" 
  element={<JobSchedulerPage />}
/>
```

### 6.2 Update `src/components/basic/Sidebar.js`

Add new menu item:

```javascript
const menuItems = [
  {
    name: '🗂️ Group A',
    isCollapsible: true,
    children: [
      { name: '🏠 Home', isCollapsible: false, children: [], to: '/' },
      { name: '📊 Data Collection', isCollapsible: false, children: [], to: '/data-collect' },
      { name: '📅 Job Scheduler', isCollapsible: false, children: [], to: '/job-scheduler' }, // ← ADD THIS
      { name: '📈 Candlestick Visualization', isCollapsible: false, children: [], to: '/analyzed-visualization-candlestick' },
      // ... rest of menu items
    ],
  },
  // ... rest of groups
];
```

---

## 7. Styling: `JobSchedulerPage.css`

```css
/* src/styles/JobSchedulerPage.css */

.job-scheduler-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #1976d2;
  font-weight: 600;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.scheduler-status-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 20px;
}

.job-table-container {
  margin-top: 20px;
}

.job-row:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}

.stock-chips {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.status-chip {
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Dialog styles */
.job-dialog .MuiDialogContent-root {
  padding: 24px;
}

.stock-input-section {
  margin: 16px 0;
}

.stock-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  min-height: 40px;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* Responsive design */
@media (max-width: 768px) {
  .quick-actions {
    flex-direction: column;
  }
  
  .quick-actions button {
    width: 100%;
  }
}
```

---

## 8. User Flow

### 8.1 Create Job Flow

```
1. User clicks "Create New Job" button
2. Dialog opens with form
3. User enters:
   - Job name (e.g., "Daily Tech Stocks")
   - Stock IDs (AAPL, MSFT, GOOGL)
   - Schedule time (17:00)
   - Optional: Start/End dates
4. User clicks "Create Job"
5. Frontend calls POST /scheduler/jobs
6. Dialog closes, success message shown
7. Jobs table refreshes automatically
8. New job appears in list
```

### 8.2 Edit Job Flow

```
1. User clicks edit icon on job row
2. Edit dialog opens with pre-filled data
3. User modifies fields
4. User clicks "Update Job"
5. Frontend calls PUT /scheduler/jobs/{id}
6. Dialog closes, success message shown
7. Jobs table refreshes
8. Updated job shown with new values
```

### 8.3 Start/Stop Job Flow

```
1. User clicks play/stop icon
2. Frontend calls POST /scheduler/jobs/{id}/start or /stop
3. Icon toggles immediately
4. Jobs table refreshes
5. Status chip updates
```

---

## 9. Features Breakdown

### Core Features (MVP)
- ✅ View all scheduled jobs in table
- ✅ Create new scheduled job
- ✅ Edit existing job
- ✅ Delete job
- ✅ Start/stop job
- ✅ View scheduler status
- ✅ Filter active jobs
- ✅ Auto-refresh every 30s

### Nice-to-Have Features (Future)
- [ ] Job execution history chart
- [ ] Email notifications setup
- [ ] Job templates
- [ ] Bulk operations (delete multiple jobs)
- [ ] Export jobs as JSON
- [ ] Import jobs from JSON
- [ ] Job cloning
- [ ] Advanced filters (by status, by stock)
- [ ] Search functionality

---

## 10. Error Handling

### API Error Handling

```javascript
try {
  await createScheduledJob(payload);
  setSuccess('Job created successfully');
} catch (err) {
  if (err.response?.status === 400) {
    setError('Invalid job configuration. Please check your inputs.');
  } else if (err.response?.status === 404) {
    setError('Scheduler service not available.');
  } else if (err.response?.status === 500) {
    setError('Server error. Please try again later.');
  } else {
    setError(`Failed to create job: ${err.message}`);
  }
}
```

### Validation Errors

```javascript
// Client-side validation before API call
const validateJob = (formData) => {
  if (!formData.name || formData.name.trim() === '') {
    return 'Job name is required';
  }
  
  if (formData.stock_ids.length === 0) {
    return 'At least one stock ID is required';
  }
  
  if (!/^([01]\d|2[0-3]):([0-5]\d)$/.test(formData.schedule_time)) {
    return 'Invalid time format. Use HH:MM';
  }
  
  return null;
};
```

---

## 11. Testing Checklist

### Component Testing
- [ ] JobSchedulerPage renders correctly
- [ ] Jobs table displays data
- [ ] Create dialog opens and closes
- [ ] Edit dialog pre-fills data
- [ ] Status card shows correct status
- [ ] Error messages display
- [ ] Success messages display

### Integration Testing
- [ ] Create job API call works
- [ ] Update job API call works
- [ ] Delete job API call works
- [ ] Start/stop job API calls work
- [ ] List jobs API call works
- [ ] Status API call works

### UI/UX Testing
- [ ] Responsive on mobile
- [ ] Buttons are clickable
- [ ] Dialogs are modal
- [ ] Table is scrollable
- [ ] Auto-refresh works
- [ ] Loading states show
- [ ] Empty state shows when no jobs

---

## 12. Implementation Timeline

### Phase 1 (Day 1-2): Core Components
- [ ] Create JobSchedulerPage component
- [ ] Create JobsTable component
- [ ] Create SchedulerStatusCard component
- [ ] Add API functions to api.js
- [ ] Add route to App.js
- [ ] Add menu item to Sidebar.js

### Phase 2 (Day 3): Dialogs
- [ ] Create JobCreationDialog component
- [ ] Create JobEditDialog component
- [ ] Implement form validation
- [ ] Add styling

### Phase 3 (Day 4): Polish
- [ ] Add error handling
- [ ] Add loading states
- [ ] Add success messages
- [ ] Test all features
- [ ] Responsive design

### Phase 4 (Day 5): Testing & Documentation
- [ ] Integration testing
- [ ] User acceptance testing
- [ ] Documentation
- [ ] Code review

---

## 13. Dependencies

### Already Available:
✅ React 18.2.0
✅ Material-UI 5.15.2
✅ Axios 1.5.1
✅ React Router DOM 6.16.0
✅ date-fns 2.30.0

### No New Dependencies Needed!

---

## 14. Mockup Structure

```
┌─────────────────────────────────────────────────────────────┐
│  📅 Job Scheduler                                            │
│  Manage scheduled jobs for automatic stock data fetching   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌───────────────────────────────┐   │
│  │ Scheduler Status │  │  [Create New Job] [Refresh]   │   │
│  │  ✅ Running      │  │  [Active Only]                │   │
│  │                  │  └───────────────────────────────┘   │
│  │  Total Jobs: 5   │                                       │
│  │  Active: 3       │                                       │
│  └──────────────────┘                                       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Name        │ Stocks    │ Schedule │ Status │ Actions │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │ Daily Tech  │ AAPL MSFT │ 17:00   │ ✅     │ ⏸ ✏ 🗑   │ │
│  │ FAANG Job   │ META ...  │ 18:00   │ ⏸     │ ▶ ✏ 🗑   │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 15. Summary

This design provides a complete, production-ready UI for managing scheduled jobs:

✅ **User-Friendly:** Clean Material-UI interface  
✅ **Responsive:** Works on desktop and mobile  
✅ **Feature-Complete:** All CRUD operations  
✅ **Real-Time:** Auto-refresh and status updates  
✅ **Error-Tolerant:** Comprehensive error handling  
✅ **Consistent:** Matches existing UI patterns  
✅ **No New Dependencies:** Uses existing libraries  
✅ **Well-Documented:** Clear code with comments  

**Estimated Implementation Time:** 5 days  
**Files to Create:** 7 new files  
**Files to Modify:** 2 existing files  

---

**Design Status:** ✅ Ready for Implementation  
**Last Updated:** October 21, 2025
