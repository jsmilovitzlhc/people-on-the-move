"""
Database CRUD operations for People on the Move.
"""
import json
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from .models import Company, Announcement, Post


# ============= Company Operations =============

def create_company(session: Session, name: str, domain: str = None,
                   website: str = None, aliases: List[str] = None) -> Company:
    """Create a new company."""
    company = Company(
        name=name,
        domain=domain,
        website=website,
    )
    if aliases:
        company.set_aliases(aliases)
    session.add(company)
    session.commit()
    return company


def get_company_by_name(session: Session, name: str) -> Optional[Company]:
    """Find company by exact name."""
    return session.query(Company).filter(Company.name == name).first()


def get_company_by_id(session: Session, company_id: int) -> Optional[Company]:
    """Find company by ID."""
    return session.query(Company).filter(Company.id == company_id).first()


def get_active_companies(session: Session) -> List[Company]:
    """Get all active companies."""
    return session.query(Company).filter(Company.is_active == True).all()


def search_company(session: Session, search_term: str) -> Optional[Company]:
    """Search for company by name or alias."""
    # First try exact match
    company = session.query(Company).filter(
        Company.name.ilike(f"%{search_term}%")
    ).first()

    if company:
        return company

    # Search in aliases (stored as JSON)
    companies = session.query(Company).filter(Company.is_active == True).all()
    search_lower = search_term.lower()

    for company in companies:
        aliases = company.get_aliases()
        for alias in aliases:
            if search_lower in alias.lower():
                return company

    return None


def update_company(session: Session, company_id: int, **kwargs) -> Optional[Company]:
    """Update company fields."""
    company = get_company_by_id(session, company_id)
    if company:
        for key, value in kwargs.items():
            if hasattr(company, key):
                setattr(company, key, value)
        session.commit()
    return company


# ============= Announcement Operations =============

def create_announcement(session: Session, company_id: int, person_name: str,
                        new_title: str = None, previous_title: str = None,
                        previous_company: str = None, announcement_date=None,
                        source_url: str = None, source_name: str = None,
                        raw_text: str = None) -> Announcement:
    """Create a new announcement."""
    announcement = Announcement(
        company_id=company_id,
        person_name=person_name,
        new_title=new_title,
        previous_title=previous_title,
        previous_company=previous_company,
        announcement_date=announcement_date,
        source_url=source_url,
        source_name=source_name,
        raw_text=raw_text,
        status=Announcement.STATUS_PENDING
    )
    session.add(announcement)
    session.commit()
    return announcement


def get_announcement_by_id(session: Session, announcement_id: int) -> Optional[Announcement]:
    """Get announcement by ID."""
    return session.query(Announcement).filter(Announcement.id == announcement_id).first()


def get_pending_announcements(session: Session) -> List[Announcement]:
    """Get all pending announcements."""
    return session.query(Announcement).filter(
        Announcement.status == Announcement.STATUS_PENDING
    ).order_by(Announcement.created_at.desc()).all()


def get_approved_announcements(session: Session) -> List[Announcement]:
    """Get all approved announcements ready for posting."""
    return session.query(Announcement).filter(
        Announcement.status == Announcement.STATUS_APPROVED
    ).order_by(Announcement.created_at.desc()).all()


def get_announcements_by_status(session: Session, status: str) -> List[Announcement]:
    """Get announcements by status."""
    return session.query(Announcement).filter(
        Announcement.status == status
    ).order_by(Announcement.created_at.desc()).all()


def get_recent_announcements(session: Session, days: int = 30) -> List[Announcement]:
    """Get announcements from the last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    return session.query(Announcement).filter(
        Announcement.created_at >= cutoff
    ).order_by(Announcement.created_at.desc()).all()


def check_duplicate(session: Session, company_id: int, person_name: str,
                    hours: int = 24) -> Optional[Announcement]:
    """Check if similar announcement exists within time window."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return session.query(Announcement).filter(
        and_(
            Announcement.company_id == company_id,
            Announcement.person_name.ilike(f"%{person_name}%"),
            Announcement.created_at >= cutoff
        )
    ).first()


def update_announcement_status(session: Session, announcement_id: int,
                                status: str) -> Optional[Announcement]:
    """Update announcement status."""
    announcement = get_announcement_by_id(session, announcement_id)
    if announcement:
        announcement.status = status
        announcement.updated_at = datetime.utcnow()
        session.commit()
    return announcement


def update_announcement(session: Session, announcement_id: int, **kwargs) -> Optional[Announcement]:
    """Update announcement fields."""
    announcement = get_announcement_by_id(session, announcement_id)
    if announcement:
        for key, value in kwargs.items():
            if hasattr(announcement, key):
                setattr(announcement, key, value)
        announcement.updated_at = datetime.utcnow()
        session.commit()
    return announcement


# ============= Post Operations =============

def create_post(session: Session, announcement_id: int, content: str) -> Post:
    """Create a new draft post."""
    post = Post(
        announcement_id=announcement_id,
        content=content
    )
    session.add(post)
    session.commit()
    return post


def get_post_by_id(session: Session, post_id: int) -> Optional[Post]:
    """Get post by ID."""
    return session.query(Post).filter(Post.id == post_id).first()


def get_post_for_announcement(session: Session, announcement_id: int) -> Optional[Post]:
    """Get the latest post for an announcement."""
    return session.query(Post).filter(
        Post.announcement_id == announcement_id
    ).order_by(Post.version.desc()).first()


def update_post_content(session: Session, post_id: int, content: str) -> Optional[Post]:
    """Update post content and increment version."""
    post = get_post_by_id(session, post_id)
    if post:
        post.content = content
        post.version += 1
        post.updated_at = datetime.utcnow()
        session.commit()
    return post


def approve_post(session: Session, post_id: int, approved_by: str) -> Optional[Post]:
    """Approve a post."""
    post = get_post_by_id(session, post_id)
    if post:
        post.approved_by = approved_by
        post.approved_at = datetime.utcnow()
        post.updated_at = datetime.utcnow()

        # Also update announcement status
        update_announcement_status(session, post.announcement_id, Announcement.STATUS_APPROVED)
        session.commit()
    return post


def mark_post_as_posted(session: Session, post_id: int,
                        linkedin_url: str = None) -> Optional[Post]:
    """Mark post as published to LinkedIn."""
    post = get_post_by_id(session, post_id)
    if post:
        post.posted_at = datetime.utcnow()
        post.linkedin_url = linkedin_url
        post.updated_at = datetime.utcnow()

        # Also update announcement status
        update_announcement_status(session, post.announcement_id, Announcement.STATUS_POSTED)
        session.commit()
    return post


# ============= Statistics =============

def get_stats(session: Session) -> dict:
    """Get summary statistics."""
    return {
        'total_companies': session.query(Company).count(),
        'active_companies': session.query(Company).filter(Company.is_active == True).count(),
        'total_announcements': session.query(Announcement).count(),
        'pending_announcements': session.query(Announcement).filter(
            Announcement.status == Announcement.STATUS_PENDING
        ).count(),
        'approved_announcements': session.query(Announcement).filter(
            Announcement.status == Announcement.STATUS_APPROVED
        ).count(),
        'posted_announcements': session.query(Announcement).filter(
            Announcement.status == Announcement.STATUS_POSTED
        ).count(),
        'total_posts': session.query(Post).count(),
    }
