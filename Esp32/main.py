import time
import machine
from bh1750 import BH1750	
from bme280 import BME280
import gc

# --- CONSTANTES DE CONFIGURAÇÃO (Fácil de ajustar) ---
TEMP_RISCO_MIN, TEMP_RISCO_MAX = 26.0, 28.0
UMID_RISCO_MIN, UMID_RISCO_MAX = 70.0, 80.0
INTERVALO_LEITURA = 5 # segundos

#inicialização do sensor BME280 (usando I2C)
i2c_bme = machine.SoftI2C(scl=machine.Pin(26), sda=machine.Pin(27))

#inicialização do sensor BH1750 (usando I2C)
i2c_luz = machine.SoftI2C(scl=machine.Pin(25), sda=machine.Pin(33))

# Variável global para monitorar a última pressão lida (para detectar quedas)
ultima_pressao = 1013.0

def classificar_risco(temp, umid, press, lux, ultima_pressao):
  
    #Condição de penumbra (luz muito baixa) - pode indicar ambiente interno ou sombra, 
    # o que é favorável para o mosquito 
    penumbra = lux < 300
    msg_luz = " (Ambiente em penumbra - Favoravel para mosquito)" if penumbra else ""
     

    # Variável auxiliar para detectar queda de pressão significativa
    queda_pressao = press < ultima_pressao - 0.5 and press < 1010
    msg_pressao = " (Pressao em queda - Alerta de Instabilidade!)" if queda_pressao else ""

    # 1. Condições Adversas (Risco Mínimo)
    if umid < 60 or temp < 14 or temp > 35:
        return "RISCO MINIMO", "Condicoes adversas ao mosquito", press
    

    # 2. Risco Máximo (Pico Ótimo + Sombra)
    if TEMP_RISCO_MIN <= temp <= TEMP_RISCO_MAX and UMID_RISCO_MIN <= umid <= UMID_RISCO_MAX:
       return "RISCO MAXIMO", "Condicoes PERFEITAS PARA PROLIFERACAO" + msg_pressao, press

    # 3. Risco Alto
    if 25 <= temp <= 30 and 70 <= umid <= 80:
        # Se a pressão estiver caindo, o Risco Alto beira o Máximo
        status = "RISCO ALTO"
        msg = "Ambiente ideal para proliferacao" + msg_pressao
        return status, msg, press

    # 4. Risco Moderado/Baixo
    if 23 <= temp <= 34 and umid >= 70:
        status = "RISCO MODERADO"
        # A queda de pressão em risco moderado é um aviso de que pode piorar logo
        msg = "Condicoes favoraveis" + msg_pressao
        return status, msg, press

    # 5. Risco Baixo
    if 23 <= temp <= 34 and 60 <= umid < 70:
        return "RISCO BAIXO", "Temperatura boa, mas umidade limitante", press    

    return "INDETERMINADO", "Fora das faixas conhecidas", press

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
        lux = sensor_luz.read()

        # Processamento
        status, descricao, ultima_pressao = classificar_risco(temp, umid, press, lux, ultima_pressao)

        # Saída
        print("-" * 40)
        print(f"[{status}] {descricao}")
        print(f"T: {temp:.1f}°C | U: {umid:.1f}% | P: {press:.1f}hPa | L: {lux:.1f}lx")
        
    except Exception as e:
        print(f"Erro na leitura: {e}") 
        
    
    
    #Espera 5 segundos antes da próxima leitura
    time.sleep(INTERVALO_LEITURA)


    
