import json
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt

# InfluxDB
token = "meu_token_secreto_123"
org = "projeto_iot"
bucket = "microclima_bucket"
influx_url = "http://localhost:8086"

influx_client = InfluxDBClient(url=influx_url, token=token, org=org)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "microclima/leituras"

def salvar_no_influx(dados: dict):
    point = (
        Point("clima")
        .tag("sensor", "esp32_01")
        .tag("status_risco", dados.get("status_risco", "DESCONHECIDO"))
        .field("temperatura", float(dados["temperatura"]))
        .field("umidade", float(dados["umidade"]))
        .field("pressao", float(dados["pressao"]))
        .field("luminosidade", float(dados["luminosidade"]))
        .time(datetime.now(timezone.utc), WritePrecision.NS)
    )
    write_api.write(bucket=bucket, org=org, record=point)
    print(f"✓ Salvo: {dados['status_risco']} | T:{dados['temperatura']:.1f}°C")

def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker MQTT (código {rc})")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        dados = json.loads(payload)
        salvar_no_influx(dados)
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

if __name__ == "__main__":
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        print("Bridge app rodando — aguardando dados do ESP32...")
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("Encerrando...")
    finally:
        mqtt_client.disconnect()
        influx_client.close()