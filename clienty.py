import socket

def iniciar_cliente():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 1. CONFIGURACIÓN DEL HOST Y PUERTO DEL SERVIDOR
    HOST = '127.0.0.1'
    PORT = 12345
    s.connect((HOST, PORT))

    try:
        # Recibir mensaje de bienvenida
        print(s.recv(1024).decode('utf-8'))
        
        # Enviar usuario
        usuario = input("Usuario > ") # Ingrese su usuario de GitHub
        s.send(usuario.encode('utf-8'))
        
        # Loop principal
        while True:
            comando = input("Comando (/repos o /adios) > ")
            # Enviar el comando
            s.send(comando.encode('utf-8'))

            # Recibir respuesta del servidor
            respuesta = s.recv(1024).decode('utf-8')
            print(respuesta)
            
            if respuesta.strip() == "adios":
                break
    
    except ConnectionRefusedError:
        print(f"Error: No se pudo conectar a {HOST}:{PORT}. Asegúrate de que el servidor esté encendido.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    iniciar_cliente()