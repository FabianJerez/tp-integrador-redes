import socket
import threading
import requests
import mysql.connector

# --- CONFIGURACIÓN ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      # Tu usuario de MySQL
    'password': '',      # Tu contraseña de MySQL
    'database': 'tp_integrador'
}

def guardar_en_db(usuario, repos, followers):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Guardar Repositorios
        for repo in repos:
            sql = "INSERT INTO repositorios (usuario, nombre_repo) VALUES (%s, %s)"
            cursor.execute(sql, (usuario, repo['name']))

        # Guardar Followers
        for follower in followers:
            sql = "INSERT INTO followers (usuario, nombre_follower) VALUES (%s, %s)"
            cursor.execute(sql, (usuario, follower['login']))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[{usuario}] Datos guardados en MySQL exitosamente.")
    except Exception as e:
        print(f"Error en base de datos: {e}")

def obtener_datos_github(usuario):
    # Nota: La API de GitHub tiene limites de uso sin token, pero sirve para pruebas
    print(f"Consultando GitHub para {usuario}...")
    repos_url = f"https://api.github.com/users/{usuario}/repos"
    followers_url = f"https://api.github.com/users/{usuario}/followers"
    
    repos = requests.get(repos_url).json()
    followers = requests.get(followers_url).json()
    
    return repos, followers

def manejar_cliente(cliente_socket, addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    usuario = ""
    
    try:
        # 1. Recibir nombre de usuario
        cliente_socket.send("Bienvenido. Ingrese su usuario de GitHub: ".encode('utf-8'))
        usuario = cliente_socket.recv(1024).decode('utf-8').strip()
        
        # 2. Obtener datos y guardar en BD
        repos, followers = obtener_datos_github(usuario)
        
        # Verificamos si GitHub devolvió error (ej. usuario no existe)
        if isinstance(repos, dict) and repos.get('message') == "Not Found":
             cliente_socket.send("Usuario no encontrado en GitHub.\n".encode('utf-8'))
        else:
            guardar_en_db(usuario, repos, followers)
            cliente_socket.send("Datos sincronizados con la Base de Datos.\nIngrese comando (/repos o /adios): ".encode('utf-8'))

            # Bucle de comandos
            while True:
                mensaje = cliente_socket.recv(1024).decode('utf-8').strip()
                
                if mensaje == "/repos":
                    # 3. Enviar lista de repositorios
                    lista_nombres = [r['name'] for r in repos]
                    respuesta = "Tus Repos:\n" + "\n".join(lista_nombres) + "\n"
                    cliente_socket.send(respuesta.encode('utf-8'))
                
                elif mensaje == "/adios":
                    # 4. Despedirse y cerrar
                    cliente_socket.send("adios".encode('utf-8'))
                    break
                
                else:
                    cliente_socket.send("Comando no reconocido. Use /repos o /adios\n".encode('utf-8'))

    except Exception as e:
        print(f"Error con el cliente {addr}: {e}")
    finally:
        print(f"[DESCONECTADO] {addr} cerró sesión.")
        cliente_socket.close()

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9999))
    server.listen()
    print("[INICIANDO] Servidor escuchando en localhost:9999")

    while True:
        client_sock, addr = server.accept()
        # Crear un hilo para concurrencia
        thread = threading.Thread(target=manejar_cliente, args=(client_sock, addr))
        thread.start()
        print(f"[CONEXIONES ACTIVAS] {threading.active_count() - 1}")

if __name__ == "__main__":
    iniciar_servidor()