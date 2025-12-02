from django.shortcuts import render
from rest_framework import viewsets, permissions, views
from django.db.models import Count, Sum
from .models import Servicio, Solicitud, Cotizacion, SolicitudHistorial
from .serializers import (
    ServicioSerializer,
    SolicitudSerializer,
    CotizacionSerializer,
    RegisterSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .utils import generar_pdf_cotizacion, enviar_notificacion_cotizacion

User = get_user_model()


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [permissions.AllowAny]


class SolicitudViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'empresa'] or user.is_staff:
            return Solicitud.objects.all()
        return Solicitud.objects.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_status = instance.estado
        new_status = serializer.validated_data.get('estado', old_status)

        if old_status != new_status:
            SolicitudHistorial.objects.create(
                solicitud=instance,
                estado_anterior=old_status,
                estado_nuevo=new_status,
                usuario_responsable=self.request.user,
                comentario="Cambio de estado automático"
            )
        
        serializer.save()


class CotizacionViewSet(viewsets.ModelViewSet):
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cotizacion = serializer.save()
        enviar_notificacion_cotizacion(cotizacion)

    @action(detail=True, methods=['get'])
    def generar_pdf(self, request, pk=None):
        cotizacion = self.get_object()
        try:
            pdf = generar_pdf_cotizacion(cotizacion)
            response = HttpResponse(pdf, content_type='application/pdf')
            
            # Check if view mode is requested
            view_mode = request.query_params.get('view', 'false')
            disposition = 'inline' if view_mode == 'true' else 'attachment'
            
            response['Content-Disposition'] = f'{disposition}; filename="cotizacion_{cotizacion.id}.pdf"'
            return response
        except ImportError as e:
            return Response({"error": str(e)}, status=500)
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error generando PDF: {error_detail}")
            return Response({"error": f"Error generando PDF: {str(e)}"}, status=500)


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = RegisterSerializer(request.user) # Reusing RegisterSerializer or create a specific one
        # Better to use a specific UserSerializer that doesn't include password logic, but RegisterSerializer output fields are fine if controlled.
        # Let's use the UserSerializer we just created in the previous step.
        from .serializers import UserSerializer
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class DashboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Base querysets
        if user.role in ['admin', 'empresa'] or user.is_staff:
            solicitudes = Solicitud.objects.all()
            cotizaciones = Cotizacion.objects.all()
        else:
            solicitudes = Solicitud.objects.filter(usuario=user)
            cotizaciones = Cotizacion.objects.filter(solicitud__usuario=user)

        # Solicitudes por estado
        solicitudes_por_estado = solicitudes.values('estado').annotate(total=Count('id'))
        
        # Total cotizado
        total_cotizado = cotizaciones.aggregate(total=Sum('monto'))['total'] or 0
        
        # Servicios más solicitados (Global or Personal?)
        # Usually "Popular Services" is a global metric, but let's keep it global for now as it's interesting info
        servicios_populares = Solicitud.objects.values('servicio__nombre').annotate(total=Count('id')).order_by('-total')

        data = {
            "solicitudes_por_estado": solicitudes_por_estado,
            "total_cotizado": total_cotizado,
            "servicios_populares": servicios_populares
        }
        return Response(data)

def index(request):
    return render(request, 'index.html')
