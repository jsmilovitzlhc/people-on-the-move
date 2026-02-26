"""
Flask routes for People on the Move dashboard.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app

from src.database.models import get_session, Announcement, Post, Company
from src.database import operations as db_ops
from src.drafting.ai_generator import generate_post

bp = Blueprint('main', __name__)


def get_db_session():
    """Get database session from app context."""
    return get_session(current_app.engine)


# ============= Web Pages =============

@bp.route('/')
def index():
    """Dashboard home page showing pending announcements."""
    session = get_db_session()
    try:
        # Get announcements grouped by status
        pending = db_ops.get_pending_announcements(session)
        approved = db_ops.get_approved_announcements(session)
        stats = db_ops.get_stats(session)

        return render_template(
            'index.html',
            pending=pending,
            approved=approved,
            stats=stats
        )
    finally:
        session.close()


@bp.route('/review/<int:announcement_id>')
def review(announcement_id):
    """Review page for a single announcement."""
    session = get_db_session()
    try:
        announcement = db_ops.get_announcement_by_id(session, announcement_id)
        if not announcement:
            flash('Announcement not found', 'error')
            return redirect(url_for('main.index'))

        # Get or generate draft post
        post = db_ops.get_post_for_announcement(session, announcement_id)
        if not post:
            # Generate draft post
            ann_data = {
                'person_name': announcement.person_name,
                'new_title': announcement.new_title,
                'company_name': announcement.company.name,
                'previous_title': announcement.previous_title,
                'raw_text': announcement.raw_text,
            }
            draft_content = generate_post(ann_data)
            post = db_ops.create_post(session, announcement_id, draft_content)

        return render_template(
            'review.html',
            announcement=announcement,
            post=post
        )
    finally:
        session.close()


@bp.route('/history')
def history():
    """View posted announcements."""
    session = get_db_session()
    try:
        posted = db_ops.get_announcements_by_status(session, 'posted')
        rejected = db_ops.get_announcements_by_status(session, 'rejected')

        return render_template(
            'history.html',
            posted=posted,
            rejected=rejected
        )
    finally:
        session.close()


@bp.route('/companies')
def companies():
    """View and manage tracked companies."""
    session = get_db_session()
    try:
        all_companies = session.query(Company).order_by(Company.name).all()
        return render_template('companies.html', companies=all_companies)
    finally:
        session.close()


# ============= API Endpoints =============

@bp.route('/api/announcements', methods=['GET'])
def api_get_announcements():
    """Get announcements with optional status filter."""
    status = request.args.get('status', 'pending')
    session = get_db_session()
    try:
        announcements = db_ops.get_announcements_by_status(session, status)
        return jsonify([{
            'id': a.id,
            'person_name': a.person_name,
            'new_title': a.new_title,
            'company': a.company.name,
            'source_url': a.source_url,
            'status': a.status,
            'created_at': a.created_at.isoformat() if a.created_at else None,
        } for a in announcements])
    finally:
        session.close()


@bp.route('/api/announcement/<int:announcement_id>/approve', methods=['POST'])
def api_approve(announcement_id):
    """Approve an announcement."""
    session = get_db_session()
    try:
        data = request.get_json() or {}
        approved_by = data.get('approved_by', 'editor')

        # Get or create post
        post = db_ops.get_post_for_announcement(session, announcement_id)
        if post:
            db_ops.approve_post(session, post.id, approved_by)
        else:
            # Just update announcement status
            db_ops.update_announcement_status(session, announcement_id, 'approved')

        return jsonify({'success': True, 'status': 'approved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/api/announcement/<int:announcement_id>/reject', methods=['POST'])
def api_reject(announcement_id):
    """Reject an announcement."""
    session = get_db_session()
    try:
        db_ops.update_announcement_status(session, announcement_id, 'rejected')
        return jsonify({'success': True, 'status': 'rejected'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/api/announcement/<int:announcement_id>/posted', methods=['POST'])
def api_mark_posted(announcement_id):
    """Mark an announcement as posted to LinkedIn."""
    session = get_db_session()
    try:
        data = request.get_json() or {}
        linkedin_url = data.get('linkedin_url')

        post = db_ops.get_post_for_announcement(session, announcement_id)
        if post:
            db_ops.mark_post_as_posted(session, post.id, linkedin_url)
        else:
            db_ops.update_announcement_status(session, announcement_id, 'posted')

        return jsonify({'success': True, 'status': 'posted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/api/post/<int:post_id>/update', methods=['POST'])
def api_update_post(post_id):
    """Update post content."""
    session = get_db_session()
    try:
        data = request.get_json() or {}
        content = data.get('content')

        if not content:
            return jsonify({'success': False, 'error': 'Content required'}), 400

        post = db_ops.update_post_content(session, post_id, content)
        if post:
            return jsonify({
                'success': True,
                'version': post.version,
                'content': post.content
            })
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/api/post/<int:post_id>/regenerate', methods=['POST'])
def api_regenerate_post(post_id):
    """Regenerate post content using AI."""
    session = get_db_session()
    try:
        post = db_ops.get_post_by_id(session, post_id)
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404

        announcement = post.announcement

        # Generate new content
        ann_data = {
            'person_name': announcement.person_name,
            'new_title': announcement.new_title,
            'company_name': announcement.company.name,
            'previous_title': announcement.previous_title,
            'raw_text': announcement.raw_text,
        }
        new_content = generate_post(ann_data, use_ai=True)

        # Update post
        post = db_ops.update_post_content(session, post_id, new_content)

        return jsonify({
            'success': True,
            'content': post.content,
            'version': post.version
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/api/stats', methods=['GET'])
def api_stats():
    """Get dashboard statistics."""
    session = get_db_session()
    try:
        stats = db_ops.get_stats(session)
        return jsonify(stats)
    finally:
        session.close()


@bp.route('/api/announcement/<int:announcement_id>', methods=['PUT'])
def api_update_announcement(announcement_id):
    """Update announcement fields."""
    session = get_db_session()
    try:
        data = request.get_json() or {}

        # Only allow updating certain fields
        allowed_fields = ['person_name', 'new_title', 'previous_title', 'previous_company']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400

        announcement = db_ops.update_announcement(session, announcement_id, **update_data)
        if announcement:
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Announcement not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()
