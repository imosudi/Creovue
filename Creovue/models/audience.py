# models/audience.py
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import db


# 
class AudienceInsight(db.Model):
    __tablename__ = 'audience_insights'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    channel_id = Column(String(50), nullable=False)
    age_demographics = Column(Text)  # JSON string
    gender_demographics = Column(Text)  # JSON string
    geographic_data = Column(Text)  # JSON string
    device_data = Column(Text)  # JSON string
    viewing_patterns = Column(Text)  # JSON string
    engagement_patterns = Column(Text)  # JSON string
    retention_data = Column(Text)  # JSON string
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="audience_insights")

class ContentPlan(db.Model):
    __tablename__ = 'content_plans'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    planned_date = Column(DateTime)
    category = Column(String(100))
    target_keywords = Column(Text)  # JSON string
    status = Column(String(50), default='planned')  # planned, in_progress, completed
    video_id = Column(String(50))  # Set when video is uploaded
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", backref="content_plans")

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    alert_type = Column(String(50), nullable=False)  # subscriber_milestone, view_drop, etc.
    condition = Column(Text, nullable=False)  # JSON string with conditions
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="alerts")

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    goal_type = Column(String(50), nullable=False)  # subscribers, views, revenue, etc.
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0)
    target_date = Column(DateTime)
    status = Column(String(50), default='active')  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", backref="goals")

