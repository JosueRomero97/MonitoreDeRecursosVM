from pymongo import MongoClient
import numpy as np
from fastapi import FastAPI



def obtener_data_BD():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['monitoreo']
    
    coleccion = db['resultados']
    ultimo_documento = coleccion.find_one(sort=[('_id', -1)])
    # print(ultimo_documento)
    return ultimo_documento


def mejor_vm(datos_vm):
    mejor_vm_nombre = None
    mejor_vm_recursos = None
    mejor_puntuacion = float('-inf')  # Inicializar con un valor negativo infinito
    
    for vm, datos in datos_vm.items():
        if vm == '_id':  # Ignorar el campo _id
            continue
        # Calcular la puntuación considerando CPU, RAM y almacenamiento
        puntuacion = (
            datos["cpu"]["core"]["media"] +
            datos["memoria"]["media"] +
            datos["storage"]["media"]
        )

        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_vm_nombre = vm
            mejor_vm_recursos = datos

    return mejor_vm_nombre, mejor_vm_recursos

def imprimir_tabla(recursos):
    print(f"{'Recurso': <15}{'Valor': <15}")
    print("-" * 30)
    for recurso, valor in recursos.items():
        print(f"{str(recurso): <15}{str(valor): <15}")

app = FastAPI()

@app.get("/recursos")
def read_root():
    resultado  = obtener_data_BD()
    mejor_vm_nombre, mejor_vm_recursos = mejor_vm(resultado)

    return {"data": "recursos","mejorVM":mejor_vm_nombre,"recursos":mejor_vm_recursos}


if __name__ == '__main__':
    # resultado  = obtener_data_BD()
    # mejor_vm_nombre, mejor_vm_recursos = mejor_vm(resultado)

    # print(f"La mejor VM es: {mejor_vm_nombre}")
    # imprimir_tabla(mejor_vm_recursos)
    import uvicorn

    uvicorn.run(app, host="10.0.10.2", port=8700)

    