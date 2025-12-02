import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from asistencia_app.models import Cotizacion

count = Cotizacion.objects.count()
print(f"Total Cotizaciones: {count}")

if count == 0:
    print("No cotizaciones found. Creating a dummy one for testing if possible.")
    # We might need to create a user and service first if we want to create a dummy one
    # But for now let's just report it.

for c in Cotizacion.objects.all():
    print(f"ID: {c.id}, Monto: {c.monto}, Fecha: {c.fecha_generada}")
    try:
        from asistencia_app.utils import generar_pdf_cotizacion
        pdf = generar_pdf_cotizacion(c)
        print(f"  [OK] PDF Generated for ID {c.id}, Size: {len(pdf)}")
    except Exception as e:
        print(f"  [ERROR] Failed to generate PDF for ID {c.id}: {e}")
