# models/channel_health.py
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import db

class ChannelHealth(db.Model):
    __tablename__ = 'channel_health'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    channel_id = Column(String(50), nullable=False)
    health_score = Column(Float, nullable=False)
    subscriber_growth_rate = Column(Float)
    view_growth_rate = Column(Float)
    engagement_rate = Column(Float)
    upload_consistency = Column(Float)
    seo_score = Column(Float)
    recommendations = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="channel_health")

class VideoPerformance(db.Model):
    __tablename__ = 'video_performance'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    video_id = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    watch_time = Column(Float, default=0)
    ctr = Column(Float, default=0)
    avg_view_duration = Column(Float, default=0)
    engagement_rate = Column(Float, default=0)
    seo_score = Column(Float, default=0)
    upload_date = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="video_performances")

class CompetitorAnalysis(db.Model):
    __tablename__ = 'competitor_analysis'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    competitor_channel_id = Column(String(50), nullable=False)
    competitor_name = Column(String(255), nullable=False)
    subscriber_count = Column(Integer, default=0)
    avg_views = Column(Float, default=0)
    upload_frequency = Column(Float, default=0)
    engagement_rate = Column(Float, default=0)
    growth_rate = Column(Float, default=0)
    content_categories = Column(Text)
    last_analyzed = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", backref="competitor_analyses")

