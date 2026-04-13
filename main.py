import time
import gc

print("Iniciando loop principal do dispositivo...")

while True:
    #Simulação de leituras de dados (já que não temos sensores conectados)
    print("--- Nova Leitura ---")
    print("Status: Sistema Operacional")

    #Garbage Coollector: Limpando a memória RAM do ESP32
    gc.collect()
    print(f"Memória RAM Livre: {gc.mem_free()} bytes")

    #Espera 5 segundos antes da próxima leitura
    time.sleep(5)