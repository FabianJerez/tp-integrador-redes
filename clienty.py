import socket

def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('localhost', 9999))

    try:
        # Recibir mensaje de bienvenida
        print(cliente.recv(4096).decode('utf-8'))
        
        # Enviar usuario
        usuario = input("Usuario > ")
        cliente.send(usuario.encode('utf-8'))
        
        # Loop principal
        while True:
            # Recibir respuesta del servidor
            respuesta = cliente.recv(4096).decode('utf-8')
            print(respuesta)
            
            if respuesta.strip() == "adios":
                break
            
            # Si no es adiós, pide el siguiente comando
            if "Ingrese comando" in respuesta or "Tus Repos" in respuesta or "Comando no reconocido" in respuesta:
                comando = input("Comando > ")
                cliente.send(comando.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cliente.close()

if __name__ == "__main__":
    iniciar_cliente()