import sys
import os
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from asistencia_app.models import Servicio

def assign_segments():
    print("Assigning segments to existing services...")
    
    services = Servicio.objects.all()
    
    if not services.exists():
        print("No services found. Please create some services first.")
        return
    
    # Example assignments (you can customize this)
    for service in services:
        # Assign based on keywords in the name
        name_lower = service.nombre.lower()
        
        if any(word in name_lower for word in ['vehiculo', 'auto', 'carro', 'moto', 'flota', 'pc', 'soporte', 'tecnico']):
            service.segmento = 'cartech'
        elif any(word in name_lower for word in ['comida', 'alimento', 'restaurante', 'catering']):
            service.segmento = 'foodtech'
        elif any(word in name_lower for word in ['adulto', 'mayor', 'cuidado', 'limpieza', 'enfermeria']):
            service.segmento = 'agetech'
        else:
            # Default to cartech for now
            service.segmento = 'cartech'
        
        service.save()
        print(f"✓ {service.nombre} -> {service.segmento}")
    
    print(f"\nDone! Updated {services.count()} services.")

if __name__ == '__main__':
    assign_segments()
