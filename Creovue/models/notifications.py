# models/notifications.py
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import db


class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    weekly_reports = Column(Boolean, default=True)
    performance_alerts = Column(Boolean, default=True)
    competitor_updates = Column(Boolean, default=False)
    milestone_notifications = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", backref="notification_preferences")


