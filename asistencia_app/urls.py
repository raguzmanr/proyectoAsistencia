from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServicioViewSet,
    SolicitudViewSet,
    CotizacionViewSet,
    CotizacionViewSet,
    RegisterView,
    DashboardView,
    UserDetailView
)

router = DefaultRouter()
router.register(r'servicios', ServicioViewSet, basename='servicios')
router.register(r'solicitudes', SolicitudViewSet, basename='solicitudes')
router.register(r'cotizaciones', CotizacionViewSet, basename='cotizaciones')

urlpatterns = [
    path('', include(router.urls)),

    # Registro de usuarios
    path('register/', RegisterView.as_view(), name='register'),
    path('users/me/', UserDetailView.as_view(), name='user-detail'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
