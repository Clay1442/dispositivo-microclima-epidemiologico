import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Configurações iguais ao do Docker
token = "meu_token_secreto_123"
org = "projeto_iot"
bucket = "microclima_bucket"
url = "http://localhost:8086"

# Inicializa o Cliente
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def salvar_dado_mock(valor_temp):
    point = Point("clima") \
        .tag("sensor", "esp32_teste") \
        .field("temperatura", valor_temp) \
        .time(datetime.utcnow(), WritePrecision.NS)
    
    write_api.write(bucket=bucket, org=org, record=point)
    print(f"Sucesso: Temperatura {valor_temp} salva no InfluxDB!")

# Teste simples
if __name__ == "__main__":
    try:
        while True:
            salvar_dado_mock(25.5) # Enviando um valor fixo para testar
            time.sleep(10)
    except KeyboardInterrupt:
        print("Finalizado.")