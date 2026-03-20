from flask import render_template, redirect, url_for, flash, request, Blueprint, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Event, EventAttendance
from app.forms import EventForm, EventApprovalForm
from datetime import datetime, date, time, timedelta
from functools import wraps

bp = Blueprint('events', __name__, url_prefix='/events')


# Decorator for faculty-only routes
def faculty_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_approve_events():
            flash('You need faculty privileges to access this page.', 'danger')
            return redirect(url_for('events.index'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/')
@login_required
def index():
    """Events home page - shows upcoming events"""
    view = request.args.get('view', 'list')  # list, calendar

    # Get upcoming approved events
    upcoming = Event.query.filter(
        Event.status == 'approved',
        Event.start_date >= datetime.utcnow()
    ).order_by(Event.start_date.asc()).limit(20).all()

    # Get featured/recommended events
    featured = Event.query.filter(
        Event.status == 'approved',
        Event.start_date >= datetime.utcnow()
    ).order_by(Event.attendee_count().desc()).limit(5).all()

    return render_template('events/index.html',
                           upcoming=upcoming,
                           featured=featured,
                           view=view)


@bp.route('/calendar')
@login_required
def calendar():
    """Calendar view of events"""
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', datetime.utcnow().month, type=int)

    # Get events for this month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    events = Event.query.filter(
        Event.status == 'approved',
        Event.start_date >= start_date,
        Event.start_date <= end_date
    ).order_by(Event.start_date.asc()).all()

    # Group events by date
    events_by_date = {}
    for event in events:
        date_key = event.start_date.strftime('%Y-%m-%d')
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)

    return render_template('events/calendar.html',
                           events_by_date=events_by_date,
                           year=year,
                           month=month,
                           now=datetime.utcnow())


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new event (multi-step form)"""
    form = EventForm()

    # Pre-fill organizer details from user profile
    if request.method == 'GET':
        form.organizer_name.data = current_user.get_full_name()
        form.contact_email.data = current_user.email

    if form.validate_on_submit():
        # Combine date and time
        start_datetime = datetime.combine(
            form.start_date.data,
            form.start_time.data or time(0, 0)
        )

        end_datetime = None
        if form.end_date.data:
            end_datetime = datetime.combine(
                form.end_date.data,
                form.end_time.data or time(23, 59)
            )

        # Create event
        event = Event(
            title=form.title.data,
            description=form.description.data,
            event_type=form.event_type.data,
            start_date=start_datetime,
            end_date=end_datetime,
            all_day=form.all_day.data,
            venue=form.venue.data,
            room=form.room.data,
            campus=form.campus.data,
            is_virtual=form.is_virtual.data,
            virtual_link=form.virtual_link.data,
            organizer_name=form.organizer_name.data,
            contact_email=form.contact_email.data,
            contact_phone=form.contact_phone.data,
            organizer_website=form.organizer_website.data,
            target_audience=form.target_audience.data,
            max_attendees=form.max_attendees.data,
            requires_registration=form.requires_registration.data,
            registration_link=form.registration_link.data,
            cost_info=form.cost_info.data,
            user_id=current_user.id,
            status='pending'  # Needs approval
        )

        db.session.add(event)
        db.session.commit()

        flash('Your event has been submitted for approval! You will be notified once it\'s approved.', 'success')
        return redirect(url_for('events.my_events'))

    return render_template('events/create.html', form=form)


@bp.route('/<int:id>')
@login_required
def view(id):
    """View single event details"""
    event = Event.query.get_or_404(id)

    # Check if event is approved or user is creator/faculty
    if event.status != 'approved' and event.user_id != current_user.id and not current_user.can_approve_events():
        flash('This event is not yet approved.', 'warning')
        return redirect(url_for('events.index'))

    # Get user's attendance status
    user_status = event.user_status(current_user.id)

    # Get attendee list (for organizers)
    attendees = []
    if current_user.id == event.user_id or current_user.can_approve_events():
        attendees = event.attendees.filter_by(status='going').all()

    return render_template('events/view.html',
                           event=event,
                           user_status=user_status,
                           attendees=attendees)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit event (only creator or faculty)"""
    event = Event.query.get_or_404(id)

    # Check permissions
    if event.user_id != current_user.id and not current_user.can_approve_events():
        flash('You cannot edit this event.', 'danger')
        return redirect(url_for('events.view', id=id))

    form = EventForm()

    if request.method == 'GET':
        # Populate form with event data
        form.title.data = event.title
        form.description.data = event.description
        form.event_type.data = event.event_type
        form.start_date.data = event.start_date.date()
        form.start_time.data = event.start_date.time()
        if event.end_date:
            form.end_date.data = event.end_date.date()
            form.end_time.data = event.end_date.time()
        form.all_day.data = event.all_day
        form.venue.data = event.venue
        form.room.data = event.room
        form.campus.data = event.campus
        form.is_virtual.data = event.is_virtual
        form.virtual_link.data = event.virtual_link
        form.organizer_name.data = event.organizer_name
        form.contact_email.data = event.contact_email
        form.contact_phone.data = event.contact_phone
        form.organizer_website.data = event.organizer_website
        form.target_audience.data = event.target_audience
        form.max_attendees.data = event.max_attendees
        form.requires_registration.data = event.requires_registration
        form.registration_link.data = event.registration_link
        form.cost_info.data = event.cost_info

    if form.validate_on_submit():
        # Update event
        event.title = form.title.data
        event.description = form.description.data
        event.event_type = form.event_type.data

        start_datetime = datetime.combine(
            form.start_date.data,
            form.start_time.data or time(0, 0)
        )
        event.start_date = start_datetime

        if form.end_date.data:
            event.end_date = datetime.combine(
                form.end_date.data,
                form.end_time.data or time(23, 59)
            )
        else:
            event.end_date = None

        event.all_day = form.all_day.data
        event.venue = form.venue.data
        event.room = form.room.data
        event.campus = form.campus.data
        event.is_virtual = form.is_virtual.data
        event.virtual_link = form.virtual_link.data
        event.organizer_name = form.organizer_name.data
        event.contact_email = form.contact_email.data
        event.contact_phone = form.contact_phone.data
        event.organizer_website = form.organizer_website.data
        event.target_audience = form.target_audience.data
        event.max_attendees = form.max_attendees.data
        event.requires_registration = form.requires_registration.data
        event.registration_link = form.registration_link.data
        event.cost_info = form.cost_info.data
        event.updated_at = datetime.utcnow()

        # If edited by non-faculty, reset to pending
        if not current_user.can_approve_events():
            event.status = 'pending'

        db.session.commit()

        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view', id=id))

    return render_template('events/edit.html', form=form, event=event)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete event (only creator or admin)"""
    event = Event.query.get_or_404(id)

    if event.user_id != current_user.id and not current_user.can_approve_events():
        flash('You cannot delete this event.', 'danger')
        return redirect(url_for('events.view', id=id))

    db.session.delete(event)
    db.session.commit()

    flash('Event deleted successfully.', 'success')
    return redirect(url_for('events.index'))


@bp.route('/<int:id>/attend', methods=['POST'])
@login_required
def attend(id):
    """RSVP to event"""
    event = Event.query.get_or_404(id)

    if event.status != 'approved':
        flash('This event is not yet approved.', 'warning')
        return redirect(url_for('events.view', id=id))

    status = request.form.get('status', 'going')

    # Check if already attending
    attendance = EventAttendance.query.filter_by(
        user_id=current_user.id,
        event_id=id
    ).first()

    if attendance:
        attendance.status = status
        attendance.updated_at = datetime.utcnow()
    else:
        attendance = EventAttendance(
            user_id=current_user.id,
            event_id=id,
            status=status
        )
        db.session.add(attendance)

    db.session.commit()

    flash(f'You are now {status} to this event!', 'success')
    return redirect(url_for('events.view', id=id))


@bp.route('/my-events')
@login_required
def my_events():
    """Show events created by current user"""
    created = Event.query.filter_by(user_id=current_user.id).order_by(Event.created_at.desc()).all()

    # Events user is attending
    attending_ids = [a.event_id for a in current_user.event_attendances.filter_by(status='going').all()]
    attending = Event.query.filter(Event.id.in_(attending_ids)).order_by(Event.start_date.asc()).all()

    return render_template('events/my_events.html',
                           created=created,
                           attending=attending)


@bp.route('/faculty/pending')
@login_required
@faculty_required
def pending_approvals():
    """Faculty dashboard - view pending events"""
    pending = Event.query.filter_by(status='pending').order_by(Event.created_at.asc()).all()
    return render_template('events/pending.html', events=pending)


@bp.route('/faculty/<int:id>/approve', methods=['POST'])
@login_required
@faculty_required
def approve(id):
    """Approve an event"""
    event = Event.query.get_or_404(id)

    event.status = 'approved'
    event.approved_by = current_user.id
    event.approved_at = datetime.utcnow()
    db.session.commit()

    # TODO: Send notification to event creator

    flash('Event approved successfully!', 'success')
    return redirect(url_for('events.pending_approvals'))


@bp.route('/faculty/<int:id>/reject', methods=['POST'])
@login_required
@faculty_required
def reject(id):
    """Reject an event with reason"""
    event = Event.query.get_or_404(id)
    reason = request.form.get('reason', '')

    event.status = 'rejected'
    event.rejection_reason = reason
    event.approved_by = current_user.id
    event.approved_at = datetime.utcnow()
    db.session.commit()

    # TODO: Send notification to event creator

    flash('Event rejected.', 'success')
    return redirect(url_for('events.pending_approvals'))


@bp.route('/search')
@login_required
def search():
    """Search events"""
    query = request.args.get('q', '')
    event_type = request.args.get('type', '')
    campus = request.args.get('campus', '')

    events_query = Event.query.filter(Event.status == 'approved')

    if query:
        events_query = events_query.filter(
            db.or_(
                Event.title.ilike(f'%{query}%'),
                Event.description.ilike(f'%{query}%'),
                Event.venue.ilike(f'%{query}%')
            )
        )

    if event_type:
        events_query = events_query.filter(Event.event_type == event_type)

    if campus:
        events_query = events_query.filter(Event.campus == campus)

    events = events_query.order_by(Event.start_date.asc()).all()

    return render_template('events/search.html',
                           events=events,
                           query=query,
                           event_type=event_type,
                           campus=campus)