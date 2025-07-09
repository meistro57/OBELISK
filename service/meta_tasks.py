from service.celery_app import celery_app
from agent_system.agents.meta_agent import MetaAgent

@celery_app.task(name="service.meta_tasks.run_meta_check")
def run_meta_check():
    """
    Celery periodic task to invoke MetaAgent's check_and_improve.
    """
    MetaAgent().check_and_improve()
