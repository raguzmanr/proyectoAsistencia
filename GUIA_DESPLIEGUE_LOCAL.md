# Guía de Despliegue Local

Esta guía te ayudará a configurar y ejecutar el proyecto de Asistencia en tu máquina local.

## Prerrequisitos

Asegúrate de tener instalado lo siguiente:

*   **Python 3.10+**: [Descargar Python](https://www.python.org/downloads/)
*   **Git**: [Descargar Git](https://git-scm.com/downloads)

## Pasos de Instalación

### 1. Clonar el Repositorio (si no lo has hecho)

Si ya tienes la carpeta del proyecto, puedes saltar este paso. Si no:

```bash
git clone <URL_DEL_REPOSITORIO>
cd proyectoAsistencia
```

### 2. Crear un Entorno Virtual

Es recomendable usar un entorno virtual para aislar las dependencias del proyecto.

**En Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**En macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Verás que tu terminal ahora muestra `(venv)` al principio de la línea.

### 3. Instalar Dependencias

Instala las librerías necesarias listadas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configuración de Variables de Entorno (Opcional)

El proyecto está configurado para funcionar localmente con valores por defecto (usando SQLite y claves de desarrollo).

Si necesitas configurar variables específicas, puedes crear un archivo `.env` en la raíz (aunque para desarrollo local básico no es estrictamente necesario gracias a los valores por defecto en `settings.py`).

### 5. Aplicar Migraciones

Prepara la base de datos (SQLite por defecto):

```bash
python manage.py migrate
```

### 6. Crear un Superusuario

Para acceder al panel de administración de Django:

```bash
python manage.py createsuperuser
```
Sigue las instrucciones para establecer un nombre de usuario, correo y contraseña.

### 7. Ejecutar el Servidor de Desarrollo

Inicia el servidor local:

```bash
python manage.py runserver
```

Deberías ver un mensaje indicando que el servidor está corriendo en `http://127.0.0.1:8000/`.

## Verificación

1.  **Panel de Administración**: Ve a [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) e inicia sesión con el superusuario que creaste.
2.  **Documentación de la API**: Ve a [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/) (o la ruta configurada para Swagger/Redoc) para ver los endpoints disponibles.

## Solución de Problemas Comunes

*   **Error de `pip`**: Asegúrate de que tu entorno virtual está activado.
*   **Error de Base de Datos**: Si tienes problemas con SQLite, borra el archivo `db.sqlite3` y vuelve a ejecutar `python manage.py migrate`.
*   **Archivos Estáticos**: Si los estilos no cargan, intenta ejecutar `python manage.py collectstatic`.
