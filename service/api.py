from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, Set
import os

from agent_system.agent_registry import AgentRegistry
from agent_system.memory import Memory
from service.celery_app import celery_app

app = FastAPI(title="OBELISK API")
registry = AgentRegistry()
memory = Memory()
import logging

# WebSocket log broadcaster
log_subscribers: Set[WebSocket] = set()

class BroadcastHandler(logging.Handler):
    """Logging handler that broadcasts log messages to all WebSocket clients."""
    def emit(self, record):
        message = self.format(record)
        for ws in list(log_subscribers):
            try:
                import asyncio
                asyncio.create_task(ws.send_text(message))
            except Exception:
                continue

# Attach broadcast handler to root logger
root_logger = logging.getLogger()
handler = BroadcastHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
root_logger.addHandler(handler)

class TaskRequest(BaseModel):
    agent: str
    params: Dict[str, Any] = {}

class TaskStatus(BaseModel):
    id: str
    agent: str
    status: str
    result: Any = None


@app.post("/tasks", response_model=TaskStatus)
async def create_task(req: TaskRequest):
    """
    Enqueue an agent task via Celery; returns a task ID immediately.
    """
    async_result = celery_app.send_task("service.api.process_task", args=[req.agent, req.params])
    import json
    memory.add("TaskRegistry", "enqueue", json.dumps({
        "id": async_result.id,
        "agent": req.agent,
        "params": req.params,
    }))
    return TaskStatus(id=async_result.id, agent=req.agent, status=async_result.status)


@celery_app.task(name="service.api.process_task")
def process_task(task_id: str):
    db = SessionLocal()
    entry = db.query(TaskEntry).get(task_id)
    if not entry:
        db.close()
        return
    try:
        agent = registry.get_agent(entry.agent, **(entry.params or {}))
        if hasattr(agent, 'generate_architecture'):
            res = agent.generate_architecture(**entry.params)
        elif hasattr(agent, 'generate_ideas'):
            res = agent.generate_ideas(**entry.params)
        else:
            res = str(agent)
        entry.status = 'completed'
        entry.result = str(res)
        memory.add(entry.agent, 'task', entry.result)
    except Exception as e:
        entry.status = 'failed'
        entry.result = str(e)
    db.commit()
    db.close()

@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task(task_id: str):
    """
    Fetch the status and result of a Celery task by ID.
    """
    res = celery_app.AsyncResult(task_id)
    return TaskStatus(
        id=res.id,
        agent=res.task_name or "",
        status=res.status,
        result=res.result if res.status == 'SUCCESS' else None,
    )

@app.get("/memory/{agent_name}")
async def get_memory(agent_name: str, limit: int = 20):
    api_logger.info(f"Get memory: agent={agent_name} limit={limit}")
    entries = memory.query(agent=agent_name, limit=limit)
    return [
        dict(id=e.id, timestamp=e.timestamp, action=e.action, content=e.content)
        for e in entries
    ]

@app.get("/tasks_all", response_model=Dict[str, TaskStatus])
async def list_tasks_all(limit: int = 50):
    """
    List recent tasks that were enqueued (via TaskRegistry) and their status/results.
    """
    import json
    logs = memory.query(agent="TaskRegistry", limit=limit)
    out: Dict[str, TaskStatus] = {}
    for e in logs:
        rec = json.loads(e.content)
        res = celery_app.AsyncResult(rec["id"])
        out[rec["id"]] = TaskStatus(
            id=res.id,
            agent=rec.get("agent", ""),
            status=res.status,
            result=res.result if res.status == 'SUCCESS' else None,
        )
    return out
