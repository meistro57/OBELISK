import os
import sqlite3


class Memory:
    """
    Memory store for agent interactions. Uses SQLAlchemy if RELATIONAL_DSN is set,
    otherwise falls back to SQLite.
    """
    def __init__(self, db_path: str = None):
        from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        Base = declarative_base()

        class MemoryEntry(Base):
            __tablename__ = 'memories'
            id = Column(Integer, primary_key=True, autoincrement=True)
            timestamp = Column(DateTime, server_default="CURRENT_TIMESTAMP")
            project = Column(String(100), nullable=True)
            agent = Column(String(100))
            action = Column(String(100))
            content = Column(Text)

        dsn = os.getenv('RELATIONAL_DSN')
        if dsn:
            engine = create_engine(dsn)
        else:
            sqlite_path = db_path or os.getenv('MEMORY_DB_PATH', './memory.sqlite')
            engine = create_engine(f'sqlite:///{sqlite_path}')

        Base.metadata.create_all(engine)
        # ensure project column exists for legacy tables
        try:
            engine.execute('ALTER TABLE memories ADD COLUMN project TEXT')
        except Exception:
            pass
        self.Session = sessionmaker(bind=engine)
        self._MemoryEntry = MemoryEntry

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                agent TEXT,
                action TEXT,
                content TEXT
            )
            """
        )
        self.conn.commit()

    def add(self, agent: str, action: str, content: str, project: str = None):
        """
        Add a memory entry for a given agent and action with arbitrary content.
        """
        session = self.Session()
        entry = self._MemoryEntry(project=project, agent=agent, action=action, content=content)
        session.add(entry)
        session.commit()
        session.close()

    def query(self, agent: str = None, project: str = None, limit: int = 100):
        """
        Retrieve recent memory entries, optionally filtered by agent.
        Returns a list of MemoryEntry objects.
        """
        session = self.Session()
        q = session.query(self._MemoryEntry)
        if project:
            q = q.filter_by(project=project)
        if agent:
            q = q.filter_by(agent=agent)
        entries = q.order_by(self._MemoryEntry.timestamp.desc()).limit(limit).all()
        session.close()
        return entries
