import socket
import json
import threading
#import uvicorn
#import mysql.connector
from time import sleep
from datetime import datetime
import pymongo


workers =[]

def servidorSocket():

    # Configuración del servidor
    host = '10.0.0.1'
    port = 9000

    # Crea un socket del servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Vincula el socket a la dirección y el puerto
    server_socket.bind((host, port))

    # Espera conexiones entrantes
    server_socket.listen()

    print(f"Escuchando en {host}:{port}")

    while True:
        # Acepta la conexión del cliente
        client_socket, client_address = server_socket.accept()
        print(f"Conexión establecida desde {client_address[0]}")
        # print(f"Conexión establecida desde socket {client_socket}")

        # Recibe datos del cliente
        data = client_socket.recv(1024).decode('utf-8')
        print("Datos recibidos correctamente")
        json_data = json.loads(data)
        
        guardarDataBd(json_data,client_address[0])

        print("Datos en formato JSON:")
        print(json.dumps(json_data, indent=2)) 
        # Envía una respuesta al cliente
        response = "recepcion correcta de la data"
        client_socket.sendall(response.encode('utf-8'))

        # Cierra los sockets
        client_socket.close()
        # server_socket.close()

def guardarDataBd(json,ip):
    
    hora_actual = datetime.now()
    hora_formateada_mysql = hora_actual.strftime("%Y-%m-%d %H:%M:%S")
    
    jsonNoSQL={
        'hora': hora_formateada_mysql,
        'data': [json]
    }

    print("json final para mongo")
    print(jsonNoSQL)

    # Conectarse a la instancia local de MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # Seleccionar la base de datos y colección
    db = client["monitoreo"]
    worker = ip.replace(".","_")
    collection = db[worker] 

    insert_data = collection.insert_one(jsonNoSQL)
    
    client.close()
        


def monitoreoBD():
    workers=['10_0_0_30','10_0_0_40','10_0_0_50']

    print("verificando data en BD")

    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['monitoreo']

    while True:
       
        try:
            print('conexion correcta a mongo')
            for worker in workers:
                colecction  = client['monitoreo'][worker]
                cantidad_data = colecction.count_documents({})
                if cantidad_data > 100:
                    sobrante = cantidad_data-100
                    document_delete = colecction.find().sort('hora',1).limit(sobrante)

                    for doc in document_delete:
                        colecction.delete_one({'_id':doc['_id']})
                    print(f'se eliminaron el total de restantes {sobrante} de la ip : {worker}' )
            

        except Exception as e:
            print(f'Error durante monitereo db : {e}')
        sleep(10)


if __name__=="__main__":
    
    hilo_servidor = threading.Thread(target=servidorSocket)
    hilo_servidor.start()
    hilo_bd = threading.Thread(target=monitoreoBD)
    hilo_bd.start()

    

