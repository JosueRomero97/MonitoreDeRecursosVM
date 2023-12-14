import socket
import subprocess
import json
import time
from datetime import datetime  

# Configuración del cliente
host = '10.0.0.1'
port = 9000
data=''

def socketClientData(data):
    # Crea un socket del cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conéctate al servidor
    client_socket.connect((host, port))
    print(f"Conectado al servidor en {host}:{port}")

    # Envía datos al servidor
    message = data
    client_socket.sendall(message.encode('utf-8'))

    # Recibe la respuesta del servidor
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Respuesta del servidor: {response}")

    # Cierra el socket
    client_socket.close()

def data_cpu():
    comando = "inicio=$(cat /proc/stat | grep cpu | awk '{print $5}'); echo $inicio; sleep 3; fin=$(cat /proc/stat | grep cpu | awk '{print $5}'); echo $fin"
    # comando = "inicio=$(cat /proc/stat | grep 'cpu ' | awk '{print $5}'); echo $inicio; sleep 3; fin=$(cat /proc/stat | grep 'cpu ' | awk '{print $5}'); echo $fin"
    proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, text=True)
    output, _ = proceso.communicate()

        # La variable "salida" contiene el tiempo en modo "idle" como una cadena
    cadena_cpu = output.strip().split('\n')
    # print('valor de cpu')
    # print(cadena_cpu)



    cadena_uno=cadena_cpu[0].split()
    # print(cadena_uno)
    cadena_dos=cadena_cpu[1].split()
    # print(cadena_dos)
    list_cpu = []
    for i in range(int(len(cadena_uno))):
        valor = int(cadena_dos[i])-int(cadena_uno[i])
        # print(valor)
        porcentaje = round((valor/300)*100,1)
        # print(f'cpu{i}',porcentaje,'%')
        list_cpu.append(porcentaje)
        # print(list_cpu)
    return list_cpu

def data_memory():

    comando = "free -h | awk '/^Mem:/ {printf \"%s, %s, %s\\n\", $2, $3, $7}'"
    proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Leer la salida del proceso y termina
    output, _ = proceso.communicate()
    output_memory = output.decode('utf-8')
    lista_memoria = output_memory.strip().split(',')
    
    return lista_memoria

def data_storage():
    command = "lsblk -o FSSIZE,FSUSED,FSUSE% | sed -n '9'p"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Espera a que el subproceso termine y captura la salida y los errores
    output, _ = process.communicate()

    # Decodifica la salida y los errores desde bytes a cadena
    output_storage = output.decode('utf-8')

    # Divide la cadena en una lista de valores
    output_lines_storage = output_storage.split()
    print
    return output_lines_storage

if __name__ == "__main__":
    while True:
        print("recoleccion de data")
        info_data_cpu = data_cpu()
        info_data_memory = data_memory()
        info_data_storage = data_storage()

        ##FORMATO CPU
        # json_cpu={
        #     'cpu_0':info_data_cpu[0],
        #     'cpu_1':info_data_cpu[1],
        #     'cpu_2':info_data_cpu[2],
        #     'cpu_3':info_data_cpu[3],
        #     'cpu_4':info_data_cpu[4],
        # } 
        core = info_data_cpu[0] / 5
        json_cpu={
            'core':core
        }
        
        ##FORMATO MEMORIA
        json_memory ={
            'total':info_data_memory[0],
            'used':info_data_memory[1],
            'free':info_data_memory[2]
        }

        ##FORMATO STORAGE

        json_storaje = {
            'storage_size':info_data_storage[0],
            'storage_free':info_data_storage[1],
            'storage_free_por':info_data_storage[2]
        }

        ##se ordena data total
        dataTotal ={
            'storage':[json_storaje],
            'memory':[json_memory],
            'cpu':[json_cpu]
        }
        json_send = json.dumps(dataTotal)
        socketClientData(json_send)
        time.sleep(5)






