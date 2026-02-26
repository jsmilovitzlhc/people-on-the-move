"""
SQLAlchemy database models for People on the Move.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Company(Base):
    """Target companies to monitor for executive moves."""
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    domain = Column(String(255))  # Email domain from CSV
    website = Column(String(500))
    aliases = Column(Text)  # JSON array of alternative names
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    announcements = relationship("Announcement", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"

    def get_aliases(self):
        """Return aliases as a list."""
        import json
        if self.aliases:
            return json.loads(self.aliases)
        return []

    def set_aliases(self, alias_list):
        """Set aliases from a list."""
        import json
        self.aliases = json.dumps(alias_list)


class Announcement(Base):
    """Executive job change announcements."""
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    person_name = Column(String(255), nullable=False)
    new_title = Column(String(500))
    previous_title = Column(String(500))
    previous_company = Column(String(255))
    announcement_date = Column(Date)
    source_url = Column(String(1000))
    source_name = Column(String(255))
    raw_text = Column(Text)  # Original article excerpt
    status = Column(String(50), default='pending')  # pending, approved, rejected, posted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="announcements")
    posts = relationship("Post", back_populates="announcement")

    # Valid status values
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_POSTED = 'posted'

    def __repr__(self):
        return f"<Announcement(id={self.id}, person='{self.person_name}', company_id={self.company_id})>"


class Post(Base):
    """Draft and published LinkedIn posts."""
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    announcement_id = Column(Integer, ForeignKey('announcements.id'), nullable=False)
    content = Column(Text, nullable=False)  # Draft LinkedIn post
    version = Column(Integer, default=1)  # For tracking edits
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    posted_at = Column(DateTime)
    linkedin_url = Column(String(1000))  # URL of posted content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    announcement = relationship("Announcement", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, announcement_id={self.announcement_id})>"


def get_engine(database_url):
    """Create database engine."""
    return create_engine(database_url, echo=False)


def get_session(engine):
    """Create a new session."""
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(engine)
