"""
SQLAlchemy database models for OctoMaster Pro.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from loguru import logger

Base = declarative_base()


class WorkflowModel(Base):
    """Database model for workflows."""

    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(20), default="1.0")
    author = Column(String(255))

    # Workflow content (JSON)
    blocks = Column(JSON)
    connections = Column(JSON)
    settings = Column(JSON)

    # Tags
    tags = Column(JSON)  # List of strings

    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # File path
    file_path = Column(String(500))

    # Relationships
    executions = relationship("ExecutionModel", back_populates="workflow", cascade="all, delete-orphan")
    scheduled_tasks = relationship("ScheduledTaskModel", back_populates="workflow", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkflowModel(id={self.id}, name={self.name})>"


class ExecutionModel(Base):
    """Database model for workflow executions."""

    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"))

    # Execution details
    status = Column(String(20))  # running, completed, failed, cancelled
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Float)  # seconds

    # Statistics
    total_blocks = Column(Integer, default=0)
    successful_blocks = Column(Integer, default=0)
    failed_blocks = Column(Integer, default=0)

    # Results
    results = Column(JSON)  # List of block results
    variables = Column(JSON)  # Final variable state
    error_message = Column(Text)

    # Triggered by
    triggered_by = Column(String(50))  # manual, scheduled, api
    scheduled_task_id = Column(String(36), ForeignKey("scheduled_tasks.id", ondelete="SET NULL"))

    # Relationships
    workflow = relationship("WorkflowModel", back_populates="executions")
    scheduled_task = relationship("ScheduledTaskModel", back_populates="executions")

    def __repr__(self):
        return f"<ExecutionModel(id={self.id}, workflow={self.workflow_id}, status={self.status})>"


class ScheduledTaskModel(Base):
    """Database model for scheduled tasks."""

    __tablename__ = "scheduled_tasks"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"))

    # Schedule configuration
    schedule_type = Column(String(20))  # once, interval, cron, event
    enabled = Column(Boolean, default=True)

    # Schedule parameters
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    interval_seconds = Column(Integer)
    interval_minutes = Column(Integer)
    interval_hours = Column(Integer)
    interval_days = Column(Integer)
    cron_expression = Column(String(100))

    # Execution settings
    max_retries = Column(Integer, default=3)
    timeout = Column(Integer, default=3600)
    headless = Column(Boolean, default=True)

    # Notifications
    notify_on_success = Column(Boolean, default=False)
    notify_on_failure = Column(Boolean, default=True)
    notification_channels = Column(JSON)  # List of channel names

    # Statistics
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_run = Column(DateTime)
    next_run = Column(DateTime)

    # Tags
    tags = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    workflow = relationship("WorkflowModel", back_populates="scheduled_tasks")
    executions = relationship("ExecutionModel", back_populates="scheduled_task")

    def __repr__(self):
        return f"<ScheduledTaskModel(id={self.id}, name={self.name})>"


class ProfileModel(Base):
    """Database model for browser profiles."""

    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Octo Browser UUID (if synced)
    octo_uuid = Column(String(100), unique=True)

    # Profile configuration
    proxy = Column(JSON)  # Proxy settings
    fingerprint = Column(JSON)  # Fingerprint settings
    cookies = Column(JSON)  # Cookies
    bookmarks = Column(JSON)  # Bookmarks

    # Status
    status = Column(String(20), default="INACTIVE")  # ACTIVE, INACTIVE

    # Tags
    tags = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_used = Column(DateTime)
    use_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<ProfileModel(id={self.id}, title={self.title})>"


class TemplateModel(Base):
    """Database model for workflow templates."""

    __tablename__ = "templates"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    difficulty = Column(String(20))  # easy, medium, hard
    author = Column(String(255))
    version = Column(String(20), default="1.0")

    # Template configuration
    inputs = Column(JSON)  # List of input parameters
    outputs = Column(JSON)  # List of outputs
    workflow_data = Column(JSON)  # Full workflow JSON

    # Display
    icon = Column(String(10))
    preview_image = Column(String(500))
    documentation_url = Column(String(500))

    # Statistics
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    use_count = Column(Integer, default=0)

    # Tags
    tags = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<TemplateModel(id={self.id}, name={self.name})>"


class SettingModel(Base):
    """Database model for application settings."""

    __tablename__ = "settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text)
    value_type = Column(String(20))  # string, int, float, bool, json
    description = Column(Text)
    category = Column(String(50))

    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<SettingModel(key={self.key})>"


# Database initialization and session management

_engine = None
_SessionLocal = None


def init_db(database_url: str = "sqlite:///./octomaster.db", echo: bool = False):
    """
    Initialize database connection and create tables.

    Args:
        database_url: SQLAlchemy database URL
        echo: Enable SQL query logging
    """
    global _engine, _SessionLocal

    logger.info(f"Initializing database: {database_url}")

    _engine = create_engine(database_url, echo=echo)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    # Create all tables
    Base.metadata.create_all(bind=_engine)

    logger.info("Database initialized successfully")


def get_session() -> Session:
    """
    Get database session.

    Returns:
        SQLAlchemy Session

    Raises:
        RuntimeError: If database not initialized
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    return _SessionLocal()


def get_engine():
    """Get database engine."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _engine
