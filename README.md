TP Integrador de API 

Utiliza Socket con threading para multiples conexiones con clientes a traves de hilos. 
Permitiendo implementar un servidor concurrente TCP/IPv4 que interactua con la API de Github para obtener los nombres de los repositorios y los seguidores de un determinado usuario.
Esta informacion la almacena en una base de datos MySQL a traves de dos tablas: una de repositorios y otra de seguidores.

Estructura del TP

servidor.py debe ejecutarse al principio para habilitar la escucha del servidor en en host y el puerto determinado, en nuestro caso es localhost.
Esta configurado para escuchar hasta 5 clientes en cola de espera. En este archivo se encuentra la logica principal (consultar GitHub, guardar en MySQL y responder a los comandos del cliente).
Es el encargado de pedirle al cliente el nombre del usuario que desea obtener su informacion de la API de GitHub.

cliente.py su funcion es conectarse al servidor (host y puerto) para tener una comunicacion bidireccional. Debe ejecutarse luego del servidor.py. 
Pueden ejecutarse varias veces el mismo archivo simulando multiples conexiones, es decir de varios clientes. Es el encargado de enviarle al servidor el nombre del usuario de GitHub y de enviar el comando deseado (/repos o /adios).

Requisitos
python 3.x
xampp (servidor con base de datos mysql)

Librerias
pip install requests mysql-connector-python

Creacion de la base de datos: tp_integrador 

paso 1: Iniciar el servidor
paso 2: Iniciar el cliente
paso 3: el cliente le envia el nombre de usuario
paso 4: el cliente le envia el comando. /repos : El servidor precesa la solicitud.
                                        /adios : Se cierra la sesion con el servidor.
