"""
Database models for PushTutor bot
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from contextlib import contextmanager

from config import settings
from logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class CuratedChannel(Base):
    """Curated educational channels approved by admins"""
    __tablename__ = 'curated_channels'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    topics = Column(JSON, nullable=True)  # List of topics/tags
    level = Column(String, nullable=True)  # beginner/intermediate/advanced
    language = Column(String, default='fa')  # fa/en/mixed
    
    # Admin info
    added_by = Column(Integer, nullable=False)  # Admin user ID
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    rating = Column(Integer, default=0)  # Optional rating by admins
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'username': self.username,
            'title': self.title,
            'description': self.description,
            'topics': self.topics or [],
            'level': self.level,
            'language': self.language,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'is_active': self.is_active,
            'rating': self.rating,
        }


class ChannelSuggestion(Base):
    """Channel suggestions from users (pending admin approval)"""
    __tablename__ = 'channel_suggestions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=True)
    title = Column(String, nullable=True)
    
    # Suggestion details
    suggested_by = Column(Integer, nullable=False)  # User ID
    suggested_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(Text, nullable=True)  # Why user thinks it's good
    
    # Review status
    status = Column(String, default='pending')  # pending/approved/rejected
    reviewed_by = Column(Integer, nullable=True)  # Admin user ID
    reviewed_at = Column(DateTime, nullable=True)
    review_note = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'username': self.username,
            'title': self.title,
            'suggested_by': self.suggested_by,
            'suggested_at': self.suggested_at.isoformat() if self.suggested_at else None,
            'reason': self.reason,
            'status': self.status,
        }


class LearningPlan(Base):
    """User learning plans"""
    __tablename__ = 'learning_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    topic = Column(String, nullable=False)
    
    # Plan details
    level = Column(String, nullable=True)
    duration_weeks = Column(Integer, nullable=True)
    plan_data = Column(JSON, nullable=True)  # Full plan structure
    
    # Status
    status = Column(String, default='active')  # active/completed/abandoned
    progress = Column(Integer, default=0)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class UserInteraction(Base):
    """Track user interactions for analytics"""
    __tablename__ = 'user_interactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    interaction_type = Column(String, nullable=False)  # query/suggestion/plan_request
    content = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class ChannelMessage(Base):
    """Stores indexed messages from curated channels for search"""
    __tablename__ = 'channel_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, nullable=False, index=True)
    message_id = Column(Integer, nullable=False)

    # Message content
    text = Column(Text, nullable=True)
    text_normalized = Column(Text, nullable=True)  # For better search

    # Metadata
    date = Column(DateTime, nullable=True, index=True)
    views = Column(Integer, default=0)
    forwards = Column(Integer, default=0)

    # Media info (if any)
    has_media = Column(Boolean, default=False)
    media_type = Column(String, nullable=True)  # photo/video/document

    # Indexing metadata
    indexed_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # For fast uniqueness check
    __table_args__ = (
        # Create unique constraint on channel_id + message_id
        # to prevent duplicates
        {'sqlite_autoincrement': True}
    )

    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'message_id': self.message_id,
            'text': self.text,
            'date': self.date.isoformat() if self.date else None,
            'views': self.views,
            'forwards': self.forwards,
            'has_media': self.has_media,
            'media_type': self.media_type,
        }


class SearchIndex(Base):
    """Full-text search index for fast searching"""
    __tablename__ = 'search_index'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('channel_messages.id'), nullable=False, index=True)

    # Search tokens
    tokens = Column(Text, nullable=False)  # Space-separated normalized tokens

    # TF-IDF weights (optional, for ranking)
    weight = Column(Integer, default=1)

    indexed_at = Column(DateTime, default=datetime.utcnow)


# Database manager
class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        logger.info(f"Database initialized: {self.database_url}")
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    # Curated Channels operations
    def add_curated_channel(self, channel_id: str, title: str, added_by: int,
                          username: str = None, description: str = None,
                          topics: List[str] = None, level: str = None,
                          language: str = 'fa') -> CuratedChannel:
        """Add a new curated channel"""
        with self.get_session() as session:
            # Check if already exists
            existing = session.query(CuratedChannel).filter_by(channel_id=channel_id).first()
            if existing:
                logger.warning(f"Channel {channel_id} already exists in curated list")
                return existing
            
            channel = CuratedChannel(
                channel_id=channel_id,
                username=username,
                title=title,
                description=description,
                topics=topics or [],
                level=level,
                language=language,
                added_by=added_by,
            )
            session.add(channel)
            session.flush()
            logger.info(f"Added curated channel: {title} ({channel_id})")
            return channel
    
    def get_curated_channels(self, topics: List[str] = None, level: str = None,
                           language: str = None, active_only: bool = True) -> List[CuratedChannel]:
        """Get curated channels with optional filters"""
        with self.get_session() as session:
            query = session.query(CuratedChannel)
            
            if active_only:
                query = query.filter_by(is_active=True)
            
            if level:
                query = query.filter_by(level=level)
            
            if language:
                query = query.filter_by(language=language)
            
            channels = query.order_by(CuratedChannel.rating.desc()).all()
            
            # Filter by topics if provided
            if topics:
                channels = [c for c in channels if c.topics and any(t in c.topics for t in topics)]
            
            return channels
    
    def remove_curated_channel(self, channel_id: str) -> bool:
        """Remove a curated channel"""
        with self.get_session() as session:
            channel = session.query(CuratedChannel).filter_by(channel_id=channel_id).first()
            if channel:
                session.delete(channel)
                logger.info(f"Removed curated channel: {channel_id}")
                return True
            return False
    
    # Channel Suggestions operations
    def add_suggestion(self, channel_id: str, suggested_by: int,
                      username: str = None, title: str = None,
                      reason: str = None) -> ChannelSuggestion:
        """Add a new channel suggestion"""
        with self.get_session() as session:
            suggestion = ChannelSuggestion(
                channel_id=channel_id,
                username=username,
                title=title,
                suggested_by=suggested_by,
                reason=reason,
            )
            session.add(suggestion)
            session.flush()
            logger.info(f"Added channel suggestion: {channel_id} by user {suggested_by}")
            return suggestion
    
    def get_pending_suggestions(self) -> List[ChannelSuggestion]:
        """Get all pending suggestions"""
        with self.get_session() as session:
            return session.query(ChannelSuggestion).filter_by(status='pending').all()
    
    def approve_suggestion(self, suggestion_id: int, reviewed_by: int,
                          add_to_curated: bool = True, **curated_kwargs) -> bool:
        """Approve a channel suggestion"""
        with self.get_session() as session:
            suggestion = session.query(ChannelSuggestion).filter_by(id=suggestion_id).first()
            if not suggestion:
                return False
            
            suggestion.status = 'approved'
            suggestion.reviewed_by = reviewed_by
            suggestion.reviewed_at = datetime.utcnow()
            
            if add_to_curated:
                self.add_curated_channel(
                    channel_id=suggestion.channel_id,
                    title=suggestion.title or f"Channel {suggestion.channel_id}",
                    added_by=reviewed_by,
                    username=suggestion.username,
                    **curated_kwargs
                )
            
            logger.info(f"Approved suggestion: {suggestion_id}")
            return True
    
    def reject_suggestion(self, suggestion_id: int, reviewed_by: int, note: str = None) -> bool:
        """Reject a channel suggestion"""
        with self.get_session() as session:
            suggestion = session.query(ChannelSuggestion).filter_by(id=suggestion_id).first()
            if not suggestion:
                return False
            
            suggestion.status = 'rejected'
            suggestion.reviewed_by = reviewed_by
            suggestion.reviewed_at = datetime.utcnow()
            suggestion.review_note = note
            
            logger.info(f"Rejected suggestion: {suggestion_id}")
            return True

    # Channel Messages operations
    def add_message(self, channel_id: str, message_id: int, text: str = None,
                   date: datetime = None, views: int = 0, forwards: int = 0,
                   has_media: bool = False, media_type: str = None) -> Optional[ChannelMessage]:
        """Add a message to the index"""
        with self.get_session() as session:
            # Check if message already exists
            existing = session.query(ChannelMessage).filter_by(
                channel_id=channel_id,
                message_id=message_id
            ).first()

            if existing:
                # Update existing message
                if text:
                    existing.text = text
                    existing.text_normalized = self._normalize_text(text)
                existing.views = views
                existing.forwards = forwards
                existing.last_updated = datetime.utcnow()
                return existing

            # Create new message
            message = ChannelMessage(
                channel_id=channel_id,
                message_id=message_id,
                text=text,
                text_normalized=self._normalize_text(text) if text else None,
                date=date,
                views=views,
                forwards=forwards,
                has_media=has_media,
                media_type=media_type,
            )
            session.add(message)
            session.flush()
            return message

    def search_messages(self, query: str, channel_ids: List[str] = None,
                       limit: int = 50) -> List[ChannelMessage]:
        """Search messages with full-text search"""
        with self.get_session() as session:
            # Normalize query
            normalized_query = self._normalize_text(query)
            if not normalized_query:
                return []

            # Build base query
            db_query = session.query(ChannelMessage)

            # Filter by channels if specified
            if channel_ids:
                db_query = db_query.filter(ChannelMessage.channel_id.in_(channel_ids))

            # Filter messages with text
            db_query = db_query.filter(ChannelMessage.text.isnot(None))

            # Simple text search (can be improved with FTS)
            search_pattern = f"%{normalized_query}%"
            db_query = db_query.filter(
                ChannelMessage.text_normalized.like(search_pattern)
            )

            # Order by relevance (views + forwards) and date
            db_query = db_query.order_by(
                (ChannelMessage.views + ChannelMessage.forwards).desc(),
                ChannelMessage.date.desc()
            )

            return db_query.limit(limit).all()

    def get_channel_stats(self, channel_id: str) -> dict:
        """Get statistics for a channel"""
        with self.get_session() as session:
            total_messages = session.query(ChannelMessage).filter_by(
                channel_id=channel_id
            ).count()

            total_views = session.query(
                session.query(ChannelMessage.views).filter_by(
                    channel_id=channel_id
                ).label('views')
            ).scalar() or 0

            return {
                'total_messages': total_messages,
                'total_views': total_views,
                'channel_id': channel_id,
            }

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for better search"""
        if not text:
            return ""
        # Convert to lowercase and remove extra whitespace
        import re
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text


# Global database instance
db_manager = DatabaseManager()
