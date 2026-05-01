import time
import machine
from bh1750 import BH1750	
from bme280 import BME280
import gc

#inicialização do sensor BME280 (usando I2C)
i2c_bme = machine.SoftI2C(scl=machine.Pin(26), sda=machine.Pin(27))

#inicialização do sensor BH1750 (usando I2C)
i2c_luz = machine.SoftI2C(scl=machine.Pin(25), sda=machine.Pin(33))

# Inicialização dos sensores
try: 
    sensor_clima = BME280(i2c=i2c_bme)
    sensor_luz = BH1750(i2c=i2c_luz)
    print("SAVA: Todos os sensores prontos!")
except Exception as e:
    print(f"Erro na inicialização: {e}")
       

print("Iniciando loop principal do dispositivo...")

while True:
    #Simulação de leituras de dados (já que não temos sensores conectados)
    print("--- Nova Leitura ---")
    print("Status: Sistema Operacional")

    #Garbage Coollector: Limpando a memória RAM do ESP32
    gc.collect()
    print(f"Memória RAM Livre: {gc.mem_free()} bytes")
    
    try:
        # Leitura Clima (BME280)
        t, p, h = sensor_clima.read_compensated_data()
        temp = t 
        press = p / 100 # Convertendo para hPa
        umid = h 
        
        # Leitura Luminosidade (BH1750)
        lux = sensor_luz.read()
        
        print("-" * 30)
        print(f"Temp: {temp:.1f} °C | Umid: {umid:.1f} %")
        print(f"Pressão: {press:.2f} hPa")
        print(f"Luz: {lux:.2f} Lux")
        
        # Lógica Epidemiológica Simples
        if lux < 10:
            print("Status: Ambiente Escuro (Possível proliferação)")
            
    except Exception as e:
        print(f"Erro na leitura: {e}") 
   
    
    
    #Espera 5 segundos antes da próxima leitura
    time.sleep(5)


    
