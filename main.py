import time
import machine
from bmp280 import BMP280
import gc

#inicialização do sensor BMP280 (usando I2C)
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(21))
bmp = None

print("Iniciando loop principal do dispositivo...")

while True:
    #Simulação de leituras de dados (já que não temos sensores conectados)
    print("--- Nova Leitura ---")
    print("Status: Sistema Operacional")

    #Garbage Coollector: Limpando a memória RAM do ESP32
    gc.collect()
    print(f"Memória RAM Livre: {gc.mem_free()} bytes")
   
    #Inicialização do sensor BMP280
    try:
        bmp = BMP280(i2c)   
        print("Sensor BMP280 inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar o sensor BMP280: {e}")

    #realiza a leitura de temperatura, pressão e umidade do sensor BMP280, e imprime os valores no console        
    if bmp is not None:
        try:
            temperatura = bmp.temperature
            pressao = bmp.pressure
            umidade = bmp.humidity

            print(f"Temperatura: {temperatura:.2f} °C")
            print(f"Pressão: {pressao:.2f} hPa")
            print(f"Umidade: {umidade:.2f} %")
        except Exception as e:
            print(f"Erro ao ler os dados do sensor BMP280: {e}")
            bmp = None  # Reinicializa o sensor para tentar novamente na próxima leitura
            
    #Espera 5 segundos antes da próxima leitura
    time.sleep(5)


    