from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Text, Index, JSON
from datetime import datetime
from .database import Base


class CallLog(Base):
    """
    Call log model for storing call history.
    Tracks both inbound and outbound calls with status updates.
    """
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String(34), unique=True, nullable=False, index=True)
    direction = Column(String(10), nullable=False, index=True)  # 'inbound' or 'outbound'
    from_number = Column(String(20), nullable=False, index=True)
    to_number = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)  # queued, ringing, in-progress, completed, etc.
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    recording_url = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 4), nullable=True)
    price_unit = Column(String(3), nullable=True, default='USD')
    call_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' which is reserved
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_call_logs_created_at_desc', created_at.desc()),
    )

    def __repr__(self):
        return f"<CallLog(call_sid={self.call_sid}, direction={self.direction}, status={self.status})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "call_sid": self.call_sid,
            "direction": self.direction,
            "from_number": self.from_number,
            "to_number": self.to_number,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "recording_url": self.recording_url,
            "price": float(self.price) if self.price else None,
            "price_unit": self.price_unit,
            "metadata": self.call_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
