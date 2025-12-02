import sys
import os
import datetime
from unittest.mock import MagicMock

# Mock Django modules BEFORE importing utils
sys.modules['django'] = MagicMock()
sys.modules['django.core'] = MagicMock()
sys.modules['django.core.mail'] = MagicMock()
sys.modules['django.conf'] = MagicMock()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Now try to import the function
    # We need to make sure we can import asistencia_app.utils
    # If asistencia_app imports other django stuff at top level, we might need to mock those too
    # Let's try to verify reportlab directly first within the function context
    from asistencia_app.utils import generar_pdf_cotizacion
    print("Successfully imported generar_pdf_cotizacion")
except ImportError as e:
    print(f"Failed to import utils: {e}")
    # Fallback: check reportlab directly
    try:
        import reportlab
        print("ReportLab is installed.")
    except ImportError:
        print("ReportLab is NOT installed.")
    sys.exit(1)

# Mock objects
mock_cotizacion = MagicMock()
mock_cotizacion.id = 123
mock_cotizacion.fecha_generada = datetime.datetime.now()
mock_cotizacion.monto = 1500.00
mock_cotizacion.solicitud.usuario.username = "TestUser"
mock_cotizacion.solicitud.servicio.nombre = "Test Service"
mock_cotizacion.solicitud.descripcion = "Test Description"
mock_cotizacion.solicitud.datos_formulario = {"Color": "Red", "Size": "Large"}

try:
    pdf_bytes = generar_pdf_cotizacion(mock_cotizacion)
    print(f"PDF generated successfully. Size: {len(pdf_bytes)} bytes")
    
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("Saved to test_output.pdf")
    
except Exception as e:
    print(f"Error generating PDF: {e}")
    # Check if it's the specific reportlab error from the function
    if "reportlab" in str(e):
        print("Confirmed: ReportLab missing or failed.")
    sys.exit(1)
