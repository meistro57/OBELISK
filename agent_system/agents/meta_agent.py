import time

from agent_system.agent_registry import AgentRegistry
from agent_system.logging import ReasoningLog
from agent_system.memory import Memory


class MetaAgent:
    """
    Oversees task outcomes, self-scores them using SelfScoringAgent,
    and re-submits tasks below a quality threshold.
    """
    def __init__(self, threshold: float = 6.0, poll_interval: int = 60):
        self.registry = AgentRegistry()
        self.memory = Memory()
        self.rl = ReasoningLog(self.memory)
        self.threshold = threshold
        self.poll_interval = poll_interval

    def check_and_improve(self):
        """
        Perform one pass: retrieve recent tasks from memory, self-score them,
        and auto-resubmit those below threshold.
        """
        scorer = self.registry.get_agent('SelfScoringAgent')
        for entry in self.memory.query(limit=50):
            try:
                score_data = scorer.evaluate(entry.content)
                score = float(score_data.get('score', 0))
                if score < self.threshold:
                    # Resubmit via Celery for the same agent; params not preserved currently
                    from service.celery_app import celery_app

                    new_id = celery_app.send_task(
                        'service.api.process_task', args=[entry.agent, {}]
                    ).id
                    self.rl.log('MetaAgent', 'resubmit', f'{entry.id}->{new_id}')
            except Exception:
                continue
