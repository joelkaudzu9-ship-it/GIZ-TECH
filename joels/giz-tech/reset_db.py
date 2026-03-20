# reset_db.py
from app import create_app
from app.extensions import db
from app.models import Business, Owner, Product, Message, Activity

app = create_app()
with app.app_context():
    # Drop all tables
    db.drop_all()
    print("✅ Dropped all tables")

    # Create all tables with new schema
    db.create_all()
    print("✅ Created all tables with new columns")

    # Create default business
    business = Business(
        name='GIZ-tech',
        whatsapp='265983142415',
        email='joelkaudzu9@gmail.com',
        email_notifications=True,
        whatsapp_notifications=False,
        daily_digest=False
    )
    db.session.add(business)

    # Create default owner
    owner = Owner(
        username='admin',
        email='admin@giztech.com'
    )
    owner.password = 'admin123'
    db.session.add(owner)

    db.session.commit()
    print("✅ Created default business and owner")
    print("   Username: admin")
    print("   Password: admin123")