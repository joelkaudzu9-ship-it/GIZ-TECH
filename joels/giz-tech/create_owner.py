# create_owner.py
from app import create_app
from app.extensions import db
from app.models import Owner

app = create_app()
with app.app_context():
    # Delete any existing owners to start fresh
    Owner.query.delete()
    db.session.commit()
    print("✓ Deleted existing owners")

    # Create new owner
    owner = Owner(
        username='admin',
        email='admin@giztech.com'
    )
    owner.password = 'admin123'  # This uses the setter method

    db.session.add(owner)
    db.session.commit()
    print("✓ New owner created")

    # Verify
    check = Owner.query.first()
    if check and check.verify_password('admin123'):
        print("\n✅ SUCCESS! Owner created and verified!")
        print(f"   Username: {check.username}")
        print(f"   Password: admin123")
        print(f"   Email: {check.email}")
    else:
        print("\n❌ Something went wrong - verification failed")