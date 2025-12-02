import requests
import json

# URL del servidor
base_url = "http://localhost:8082"

print("=" * 60)
print("GENERADOR DE TOKEN - API DE ASISTENCIA")
print("=" * 60)

# Solicitar credenciales
username = input("\nIngresa tu username: ")
password = input("Ingresa tu password: ")

# Generar token
print("\nGenerando token...")
try:
    response = requests.post(
        f"{base_url}/api/token/",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access")
        refresh_token = data.get("refresh")
        
        print("\n✅ TOKEN GENERADO EXITOSAMENTE!\n")
        print("=" * 60)
        print("ACCESS TOKEN:")
        print("=" * 60)
        print(access_token)
        print("\n" + "=" * 60)
        print("PARA USAR EN SWAGGER UI, COPIA ESTO COMPLETO:")
        print("=" * 60)
        print(f"Bearer {access_token}")
        print("\n" + "=" * 60)
        
        # Guardar en archivo
        with open("token.txt", "w") as f:
            f.write(f"Bearer {access_token}")
        
        print("\n✅ Token guardado en 'token.txt'")
        
        # Probar el token
        print("\n🔍 Probando el token...")
        test_response = requests.get(
            f"{base_url}/api/solicitudes/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if test_response.status_code == 200:
            print("✅ ¡El token funciona correctamente!")
            print(f"   Solicitudes encontradas: {len(test_response.json())}")
        else:
            print(f"⚠️  Código de respuesta: {test_response.status_code}")
            print(f"   Respuesta: {test_response.text}")
    else:
        print(f"\n❌ Error al generar token")
        print(f"   Código: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
input("\nPresiona ENTER para salir...")
