from rest_framework import serializers
from .models import Servicio, Solicitud, Cotizacion, SolicitudHistorial
from django.contrib.auth import get_user_model

# -----------------------------
# Servicio
# -----------------------------
class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'


# -----------------------------
# Solicitud
# -----------------------------
class SolicitudHistorialSerializer(serializers.ModelSerializer):
    usuario_responsable_nombre = serializers.ReadOnlyField(source='usuario_responsable.username')

    class Meta:
        model = SolicitudHistorial
        fields = '__all__'


class SolicitudSerializer(serializers.ModelSerializer):
    historial = SolicitudHistorialSerializer(many=True, read_only=True)
    cotizacion_id = serializers.SerializerMethodField()
    cotizacion_monto = serializers.SerializerMethodField()

    class Meta:
        model = Solicitud
        fields = '__all__'
        read_only_fields = ('fecha_creacion', 'usuario')

    def get_cotizacion_id(self, obj):
        if hasattr(obj, 'cotizacion'):
            return obj.cotizacion.id
        return None

    def get_cotizacion_monto(self, obj):
        if hasattr(obj, 'cotizacion'):
            return float(obj.cotizacion.monto)
        return None


# -----------------------------
# Cotización
# -----------------------------
class CotizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cotizacion
        fields = '__all__'


# -----------------------------
# Registro de usuarios
# -----------------------------
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')
