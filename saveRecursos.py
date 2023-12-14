import json
import re
import numpy as np
from pymongo import MongoClient
import asyncio

def listMemoria(lst):
    numeros = [float(re.search(r'\d+\.\d+', elemento).group()) for elemento in lst]
    return numeros

def listaStorage(lst, total):
    # storage_total_float = float(re.search(r'\d+\.\d+', total[0]).group())
    # storage_libre_float = [float(re.search(r'\d+\.\d+', elemento).group()) for elemento in lst]
    print(lst)
    # storage_libre_float = [float(match.group()) for match in re.finditer(r'\d+(\.\d+)?', lst)]
    storage_libre_float = [float(valor[:-1]) if valor.endswith("G") else float(valor) for valor in lst]
    storage_total_float = float(re.search(r'\d+\.\d+', total[0]).group())

    respuesta = [storage_total_float - valor for valor in storage_libre_float]
    return respuesta

def mediaVarianza(lista):
    media = np.mean(lista)
    varianza = np.var(lista)
    return media, varianza

def datosWorker(colecciones, db):
    resultados = {}
    for worker in colecciones:
        resultados[worker] = {}
        
        memoria = [doc['data'][0]['memory'][0]['free'] for doc in db[worker].find().limit(100)]
        list_memoria = listMemoria(memoria)
        media1, varianza1 = mediaVarianza(list_memoria)
        resultados[worker]['memoria'] = {'media': media1, 'varianza': varianza1}
        
        storage_total = [doc['data'][0]['storage'][0]['storage_size'] for doc in db[worker].find().limit(1)]
        storage = [doc['data'][0]['storage'][0]['storage_free'] for doc in db[worker].find().limit(100)]
        list_storage = listaStorage(storage, storage_total)
        media2, varianza2 = mediaVarianza(list_storage)
        resultados[worker]['storage'] = {'media': media2, 'varianza': varianza2}
        
        resultados[worker]['cpu'] = {}
        core = [doc['data'][0]['cpu'][0]['core'] for doc in db[worker].find().limit(100)]
        mediaCPU0, varianzaCPU0 = mediaVarianza(core)
        resultados[worker]['cpu']['core'] = {'media': mediaCPU0, 'varianza': varianzaCPU0}

    print("Resultado final:")
    print(resultados)
    return resultados

def sendDataBD(resultado, db):
    json_resolt = json.dumps(resultado)
    coleccion = db['resultados']
    coleccion.insert_one(json.loads(json_resolt))

async def   main():
    while True:
        # Conéctate a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['monitoreo']

        # Nombres de tus colecciones
        colecciones = ['10_0_0_30', '10_0_0_40', '10_0_0_50']
        
        # Procesar datos y enviar a MongoDB
        resultados = datosWorker(colecciones, db)
        sendDataBD(resultados, db)

        # Esperar 5 segundos antes de la próxima iteración
        await asyncio.sleep(10)

if __name__ == '__main__':
    # Iniciar el bucle de eventos de asyncio
    asyncio.run(main())
