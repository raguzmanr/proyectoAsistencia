import io
from django.core.mail import EmailMessage
from django.conf import settings

def generar_pdf_cotizacion(cotizacion):
    """
    Genera un PDF para la cotización dada usando ReportLab.
    Retorna el contenido del PDF en bytes.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
    except ImportError:
        raise ImportError("La librería 'reportlab' no está instalada. Por favor instálala con: pip install reportlab")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Encabezado
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, f"Cotización #{cotizacion.id}")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 90, f"Fecha: {cotizacion.fecha_generada.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(50, height - 110, f"Cliente: {cotizacion.solicitud.usuario.username}")
    
    # Línea separadora
    p.line(50, height - 130, width - 50, height - 130)
    
    # Detalles del servicio
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 160, "Detalles del Servicio")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 185, f"Servicio: {cotizacion.solicitud.servicio.nombre}")
    p.drawString(50, height - 205, f"Descripción: {cotizacion.solicitud.descripcion}")
    
    # Datos del formulario dinámico si existen
    if cotizacion.solicitud.datos_formulario:
        datos = cotizacion.solicitud.datos_formulario
        if isinstance(datos, str):
            import json
            try:
                datos = json.loads(datos)
            except json.JSONDecodeError:
                datos = {}
        
        if isinstance(datos, dict) and datos:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, height - 235, "Información Adicional:")
            p.setFont("Helvetica", 10)
            y_position = height - 255
            for key, value in datos.items():
                p.drawString(70, y_position, f"• {key}: {value}")
                y_position -= 20
    
    # Monto total
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 350, f"Total a Pagar: ${cotizacion.monto}")

    # Pie de página
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 50, "Gracias por confiar en nuestros servicios.")
    p.drawString(50, 35, "Para cualquier consulta, contáctenos.")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def enviar_notificacion_cotizacion(cotizacion):
    """
    Envía un correo electrónico al cliente con la cotización adjunta.
    """
    subject = f"Cotización #{cotizacion.id} lista"
    message = f"Hola {cotizacion.solicitud.usuario.username},\n\nTu cotización para el servicio '{cotizacion.solicitud.servicio.nombre}' ha sido generada.\n\nAdjuntamos el PDF con los detalles.\n\nSaludos."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [cotizacion.solicitud.usuario.email]

    if not cotizacion.solicitud.usuario.email:
        print(f"El usuario {cotizacion.solicitud.usuario.username} no tiene email configurado.")
        return

    try:
        pdf_content = generar_pdf_cotizacion(cotizacion)
        email = EmailMessage(subject, message, email_from, recipient_list)
        email.attach(f'cotizacion_{cotizacion.id}.pdf', pdf_content, 'application/pdf')
        email.send()
    except Exception as e:
        print(f"Error enviando correo: {e}")
