# seeder.py
from Creovue import app, db
from Creovue.routes import user_datastore
from flask_security.utils import hash_password

from Creovue.models import User, Role  # Adjust if needed

def seed_roles_and_admin():
    with app.app_context():
        db.create_all()

        # Create roles
        for role_name in ["Admin", "Creator", "Analyst"]:
            if not Role.query.filter_by(name=role_name).first():
                user_datastore.create_role(name=role_name, description=f"{role_name} role")

        # Create admin user
        admin_email = "admin@creovue.io"
        admin_password = "Admin123!"  # Change this securely in production
        if not User.query.filter_by(email=admin_email).first():
            admin_user = user_datastore.create_user(
                username="admin",
                email=admin_email,
                password=hash_password(admin_password),
                active=True
            )
            user_datastore.add_role_to_user(admin_user, "Admin")

        db.session.commit()
        print("✅ Seeded roles and admin user.")

if __name__ == "__main__":
    seed_roles_and_admin()