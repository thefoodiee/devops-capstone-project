import os
import sys
import time

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.models import db, User, Note

def init_db():
    app = create_app()
    with app.app_context():
        print("[INIT] Creating database tables if not exist...")
        db.create_all()

        # Seed Admin user if not exists
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", email="admin@cloudnotes.local")
            admin.set_password("admin123")
            db.session.add(admin)
            print("[INIT] Created admin user (admin / admin123)")

        # Seed Demo user if not exists
        demo = User.query.filter_by(username="demo").first()
        if not demo:
            demo = User(username="demo", email="demo@cloudnotes.local")
            demo.set_password("demo123")
            db.session.add(demo)
            print("[INIT] Created demo user (demo / demo123)")

        db.session.commit()

        # Seed sample notes for demo user if none exist
        if Note.query.filter_by(user_id=demo.id).count() == 0:
            sample_notes = [
                Note(
                    user_id=demo.id,
                    title="DevOps CI/CD Pipeline Architecture",
                    content="End-to-end automated software delivery pipeline integrating:\n1. Git Version Control with GitHub Flow\n2. Jenkins automated build, security scan, and test\n3. Docker container packaging and optimization\n4. Kubernetes rolling updates & GitOps (ArgoCD)\n5. Prometheus & Grafana full-stack observability.",
                    category="DevOps",
                    is_pinned=True
                ),
                Note(
                    user_id=demo.id,
                    title="Kubernetes Cluster Cheatsheet",
                    content="Essential kubectl commands:\n- kubectl get pods -n notes-app\n- kubectl describe deployment notes-app -n notes-app\n- kubectl logs -l app=notes-app -f\n- kubectl rollout status deployment/notes-app\n- kubectl rollout undo deployment/notes-app (Rollback)",
                    category="Kubernetes",
                    is_pinned=True
                ),
                Note(
                    user_id=demo.id,
                    title="Terraform Infrastructure as Code Principles",
                    content="Modular, reproducible infrastructure provisioning using Terraform:\n- Declarative resource definitions\n- State management with locking\n- Input variables, environment separation, and outputs\n- Clean separation between network (VPC) and compute (EKS/EC2).",
                    category="Terraform",
                    is_pinned=False
                ),
                Note(
                    user_id=demo.id,
                    title="Ansible Configuration Management",
                    content="Playbooks automate node provisioning:\n- Docker CE and Docker Compose installation\n- Kubernetes cluster prerequisites configuration\n- Application deployment and config template injection\n- Idempotent execution across all inventory hosts.",
                    category="Ansible",
                    is_pinned=False
                ),
                Note(
                    user_id=demo.id,
                    title="Prometheus & Grafana Observability",
                    content="Application exports real-time metrics on /metrics:\n- notes_http_requests_total\n- notes_http_request_duration_seconds\n- notes_app_total_notes\n- notes_app_total_users\nGrafana dashboards visualize traffic rate, p95 latency, and error codes.",
                    category="DevOps",
                    is_pinned=False
                ),
            ]
            db.session.add_all(sample_notes)
            db.session.commit()
            print(f"[INIT] Seeded {len(sample_notes)} initial notes for demo user.")

        print("[INIT] Database initialization completed successfully.")

if __name__ == "__main__":
    init_db()
