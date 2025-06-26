# arionkoder-distributed-task-scheduler
This repository contains the implementation for the 'Distributed Task Scheduler' exercise.

# Usage Options
After cloning the project using the command `git clone https://github.com/BastosDiogo/arionkoder-distributed-task-scheduler.git`,  choose one of the two options below to run the project:

1-) Fully containerized application:

• Build the container image with the following command: `sudo sudo docker build -t distributed-task .`

• Then, create and run the container with the following command: `sudo docker run -p 8000:8000 distributed-task`

• Then in a browser set `http://localhost:8000/docs`

2-) Running locally:

• Create a Python virtual environment using the appropriate command for your OS (Linux or Windows) and activate it.

• Then install Poetry with `pip install poetry`, and navigate to the `app` directory and run `poetry install`;

• While still in the `app` directory, run: `uvicorn main:app --reload`. Then in a browser set `http://127.0.0.1:8000/docs`

# Running the application
1-) System Initialization
• Start the Scheduler Server (with FastAPI):
`http://localhost:8000/docs` or `http://127.0.0.1:8000/docs` (depending on how you've set up the project).


2-) Worker Registration
`POST /register_worker/{worker_id}`

Flow:

• It sends a POST request to this endpoint with its ID.

• The scheduler adds the worker to its list of active workers.

3-) Worker Health Monitoring (Heartbeat)
`PUT /heartbeat/{worker_id}`

Who uses it: Each individual worker, periodically.

Purpose: The worker informs the scheduler that it's still active and functional. This is crucial for fault tolerance, as it allows the scheduler to detect workers that have stopped responding.

Flow:

• As long as the worker is active, it sends PUT requests to this endpoint at regular intervals (e.g., every 5 seconds).

• The scheduler updates the record of the last heartbeat for that worker.

(Internally) The scheduler runs a routine that checks for workers without a recent heartbeat and marks them as inactive/failed, re-enqueuing their tasks.

4-) Adding New Tasks
`POST /add_task`

Who uses it: The system client (your application, automation script, etc.).

Purpose: Allows new units of work to be submitted to the scheduler for execution.

Flow:

• The client prepares the task data (function, arguments, priority, dependencies, timeout).

• It sends a POST request to this endpoint.

• The scheduler receives and validates the task, then adds it to its queue, considering priorities and dependencies.

5-) Task Request and Execution by the Worker
`GET /get_task/{worker_id}`

Who uses it: Each individual worker, in a continuous loop.

Purpose: The worker asks the scheduler if there are any tasks available for it to execute.

Flow:

• The worker sends a GET request to this endpoint.

• The scheduler checks the priority task queue, dependencies, and the availability of ready tasks.

• If a task is available, the scheduler marks it as "running" and sends it to the worker.

• The worker executes the task.

6-) Task Status Update
`POST /task_status`

Who uses it: Each individual worker, after completing or failing a task.

Purpose: The worker informs the scheduler about the outcome of a task's execution.

Flow:

• After task execution (success, failure, timeout), the worker sends a POST request to this endpoint.

• The scheduler updates the task's status in its record.

• If the task was COMPLETED, the scheduler checks and releases any tasks that depended on it.

• If the task FAILED or TIMED_OUT, the scheduler might re-enqueue it for retries (if configured).

7-) System Status Monitoring
`GET /status`

Who uses it: Clients, monitoring tools, or an administrator.

Purpose: To get an overview of the system's current state (number of tasks by status, active workers, etc.).

Flow:

• The client sends a GET request to this endpoint.

• The scheduler returns a consolidated report.


8-) Task Cancellation
`POST /cancel_task/{task_id}`

Who uses it: The system client.

Purpose: To request the cancellation of a specific task that is pending or running.

Flow:

• The client sends a POST request with the ID of the task to be canceled.

• The scheduler marks the task as CANCELED.


9-) Worker Deregistration (Optional, usually implicit)
`DELETE /unregister_worker/{worker_id}`

Who uses it: A worker that is being gracefully shut down, or an orchestration system.

Purpose: To explicitly inform the scheduler that a worker is no longer available.

Flow:

• The worker sends a DELETE request upon shutdown.

• The scheduler removes the worker from its list and re-enqueues any tasks it was executing.

(Alternative) In most cases, the absence of heartbeats via PUT /heartbeat would be sufficient for the scheduler to detect the failure and automatically deregister the worker.