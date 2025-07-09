from agent_system.memory import Memory


class ReasoningLog:
    """
    Logs agent reasoning steps into Memory and retrieves reasoning chains.
    """
    def __init__(self, memory: Memory):
        self.memory = memory

    def log(self, agent: str, step: str, content: str):
        """Record a reasoning step for an agent."""
        self.memory.add(agent, f"reasoning:{step}", content)

    def get_chain(self, agent: str, limit: int = 100):
        """
        Retrieve recent reasoning entries for the agent as a list of tuples.
        """
        return self.memory.query(agent=agent, limit=limit)
