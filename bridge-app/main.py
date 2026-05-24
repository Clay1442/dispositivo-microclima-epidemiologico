import json
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt

load_dotenv()

#Conexão InfluxDB
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

#Conexão MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "bridge-app")

print(f"Tentando conectar no banco: {INFLUX_URL}")
print(f"Na organização: {INFLUX_ORG}")

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def salvar_no_influx(dados: dict, write_api):
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
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print(f"✓ Salvo: {dados['status_risco']} | T:{dados['temperatura']:.1f}°C")

def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker MQTT (código {rc})")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        dados = json.loads(payload)
        salvar_no_influx(dados, userdata)
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

if __name__ == "__main__":
    mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID, userdata=write_api)
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
        print("Finalizado.")