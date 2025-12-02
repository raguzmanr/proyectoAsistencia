import sys
import os
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from asistencia_app.models import Solicitud, Cotizacion

def create_quotation():
    print("Searching for pending requests...")
    solicitud = Solicitud.objects.filter(estado='pendiente').first()
    
    if not solicitud:
        print("No pending requests found. Please create one in the app first.")
        return

    print(f"Found request #{solicitud.id} from {solicitud.usuario.username}")
    
    # Check if quotation exists
    if hasattr(solicitud, 'cotizacion'):
        print(f"Quotation already exists for request #{solicitud.id}")
        return

    # Create Quotation
    cotizacion = Cotizacion.objects.create(
        solicitud=solicitud,
        monto=150.00 # Example amount
    )
    
    # Update request status
    solicitud.estado = 'en_proceso'
    solicitud.save()
    
    print(f"Created Quotation #{cotizacion.id} for Request #{solicitud.id}")
    print("Status updated to 'en_proceso'")

if __name__ == '__main__':
    create_quotation()
