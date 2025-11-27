import socket
import threading as th
import requests
import mysql.connector

# --- CONFIGURACIÓN DE LA BASE DE DATOS---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      # usuario de MySQL
    'password': '',      # contraseña de MySQL NO TIENE
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

def manejar_cliente(cliente, addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    usuario = ""
    
    try:
        # 1. Recibir nombre de usuario
        cliente.send("Bienvenido. Ingrese su usuario de GitHub: ".encode('utf-8'))
        usuario = cliente.recv(1024).decode('utf-8').strip()
        
        # 2. Obtener datos y guardar en BD
        repos, followers = obtener_datos_github(usuario)
        
        # Verificamos si GitHub devolvió error (ej. usuario no existe)
        if repos and repos.get('message') == 'Not Found':
            cliente.send("Usuario no encontrado en GitHub.\n".encode('utf-8'))
        else:
            guardar_en_db(usuario, repos, followers)
            cliente.send("Datos sincronizados con la Base de Datos.\nIngrese comando (/repos o /adios): ".encode('utf-8'))

            # Bucle de comandos
            while True:
                mensaje = cliente.recv(1024).decode('utf-8').strip()
                
                if mensaje == "/repos":
                    # 3. Enviar lista de repositorios
                    lista_nombres = []              # 1. Creamos una lista vacía.
                    for r in repos:                 # 2. Iteramos sobre cada repositorio (r).
                        nombre = r['name']          # 3. Extraemos el nombre del diccionario.
                        lista_nombres.append(nombre) # 4. Añadimos el nombre a la lista.
                    respuesta = "Tus Repos:\n" + "\n".join(lista_nombres) + "\n" # 5. Formateamos la respuesta. columna
                    cliente.send(respuesta.encode('utf-8'))
                
                elif mensaje == "/adios":
                    # 4. Despedirse y cerrar
                    cliente.send("adios".encode('utf-8'))
                    break
                
                else:
                    cliente.send("Comando no reconocido. Use /repos o /adios\n".encode('utf-8'))

    except Exception as e:
        print(f"Error con el cliente {addr}: {e}")
    finally:
        print(f"[DESCONECTADO] {addr} cerró sesión.")
        cliente.close()

def iniciar_servidor(): #servidor base
    # 1. Creamos el socket
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#socket para ipv4 y tcp
    # 2. CONFIGURACIÓN DEL HOST Y PUERTO
    HOST = '127.0.0.1' # La IP del servidor
    PORT = 12345       # El puerto que vamos a escuchar
    servidor.bind((HOST, PORT)) #enlazo el socket con la ip y el puerto
    servidor.listen(5) #escucha 5 peticiones en cola de espera
    print(f"[INICIANDO] Servidor escuchando en {HOST}:{PORT}")

    while True:
        conexion, direccion = servidor.accept()
        # Crear un hilo para concurrencia
        thread = th.Thread(target=manejar_cliente, args=(conexion, direccion))
        thread.start()
        print(f"[CONEXIONES ACTIVAS] {th.active_count() - 1}") #resto 1 para no contar el hilo principal

if __name__ == "__main__":
    iniciar_servidor()