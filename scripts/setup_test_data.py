import sys
import os
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from asistencia_app.models import User, Servicio

def setup_data():
    print("Setting up test data...")

    # 1. Create Admin User
    admin_user, created = User.objects.get_or_create(username='admin', email='admin@example.com')
    if created:
        admin_user.set_password('admin123')
        admin_user.role = 'admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("Created admin user: admin / admin123")
    else:
        print("Admin user already exists")

    # 2. Create Client User
    client_user, created = User.objects.get_or_create(username='cliente', email='cliente@example.com')
    if created:
        client_user.set_password('cliente123')
        client_user.role = 'cliente'
        client_user.save()
        print("Created client user: cliente / cliente123")
    else:
        print("Client user already exists")

    # 3. Create Service with Schema
    s1, created = Servicio.objects.get_or_create(
        nombre='Soporte Técnico PC',
        defaults={
            'descripcion': 'Reparación y mantenimiento de computadoras.',
            'tarifa_base': 50.00,
            'form_schema': [
                {"name": "marca", "label": "Marca del equipo", "type": "text", "placeholder": "Ej: Dell, HP"},
                {"name": "tipo", "label": "Tipo de equipo", "type": "select", "options": ["Laptop", "Desktop", "Servidor"]},
                {"name": "urgencia", "label": "Nivel de urgencia", "type": "select", "options": ["Baja", "Media", "Alta"]}
            ]
        }
    )
    if created:
        print(f"Created service: {s1.nombre} with schema")
    else:
        # Update schema just in case
        s1.form_schema = [
            {"name": "marca", "label": "Marca del equipo", "type": "text", "placeholder": "Ej: Dell, HP"},
            {"name": "tipo", "label": "Tipo de equipo", "type": "select", "options": ["Laptop", "Desktop", "Servidor"]},
            {"name": "urgencia", "label": "Nivel de urgencia", "type": "select", "options": ["Baja", "Media", "Alta"]}
        ]
        s1.save()
        print(f"Updated service: {s1.nombre}")

    # 4. Create Simple Service
    s2, created = Servicio.objects.get_or_create(
        nombre='Limpieza General',
        defaults={
            'descripcion': 'Limpieza profunda de oficinas o casas.',
            'tarifa_base': 30.00,
            'form_schema': [] # No schema
        }
    )
    if created:
        print(f"Created service: {s2.nombre}")

    print("Done!")

if __name__ == '__main__':
    setup_data()
