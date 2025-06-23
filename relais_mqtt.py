#  Dit is de tweede werkende versie van het relais MQTT script voor de Raspberry Pi.

# Importeer de benodigde bibliotheken
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time

# Definieer de GPIO-pin voor de relais
RELAIS_PIN = 24

# GPIO-instellingen
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAIS_PIN, GPIO.OUT)
GPIO.output(RELAIS_PIN, GPIO.LOW) # Zorg dat de relais standaard uit staat

# MQTT-instellingen
MQTT_SERVER = "localhost" # Of het IP-adres van je Pi
MQTT_TOPIC = "relais/status"

# Functie die wordt aangeroepen wanneer een connectie is gemaakt
def on_connect(client, userdata, flags, rc):
    print(f"Verbonden met MQTT Broker met resultaatcode {rc}")
    # Abonneer op het topic zodra de connectie is gemaakt
    client.subscribe(MQTT_TOPIC)

# Functie die wordt aangeroepen wanneer een bericht wordt ontvangen
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Bericht ontvangen op topic {msg.topic}: {payload}")

    if payload == "AAN":
        GPIO.output(RELAIS_PIN, GPIO.HIGH)
        print("Relais AAN")
    elif payload == "UIT":
        GPIO.output(RELAIS_PIN, GPIO.LOW)
        print("Relais UIT")

# Maak een MQTT client-instantie
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Probeer te verbinden met de broker
try:
    client.connect(MQTT_SERVER, 1883, 60)
except ConnectionRefusedError:
    print("MQTT-connectie geweigerd. Draait de Mosquitto broker?")
    GPIO.cleanup()
    exit()

# Start een oneindige lus om berichten te verwerken
try:
    print("Wachten op MQTT-berichten... Druk op CTRL+C om te stoppen.")
    client.loop_forever()
except KeyboardInterrupt:
    print("Script gestopt.")
    GPIO.cleanup()
    client.disconnect()