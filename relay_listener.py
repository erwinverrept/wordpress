# Dit was de eerste versie.

import paho.mqtt.client as mqtt
# from gpiozero.output_devices import Relay # <-- Vorige poging gaf een error
from gpiozero import OutputDevice # <-- AANGEPAST: Gebruik een meer fundamentele klasse die altijd zou moeten werken
from time import sleep

# --- Configuratie ---
MQTT_BROKER_ADRES = "localhost"  # De broker draait op dezelfde Pi
MQTT_TOPIC = "thuis/woonkamer/relais1" # Kies een beschrijvend topic
GPIO_PIN = 24 # De BCM GPIO-pin waarop het relais is aangesloten

# Initialiseer het relais als een algemeen 'OutputDevice'.
# Dit is robuuster voor verschillende gpiozero-versies.
try:
    # We gebruiken nu OutputDevice in plaats van Relay
    relais = OutputDevice(GPIO_PIN) 
    print(f"OutputDevice op GPIO-pin {GPIO_PIN} succesvol geïnitialiseerd.")
except Exception as e:
    print(f"FATALE FOUT: Kon device op pin {GPIO_PIN} niet initialiseren: {e}")
    print("Controleer of de pin correct is en niet in gebruik is.")
    exit() # Stop het script als de pin niet werkt

# Deze functie wordt uitgevoerd zodra er verbinding is met de broker
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Succesvol verbonden met MQTT Broker!")
        # Abonneer op het topic zodra de verbinding is gemaakt
        client.subscribe(MQTT_TOPIC)
        print(f"Luistert naar topic: '{MQTT_TOPIC}'")
    else:
        print(f"Verbinding met MQTT Broker mislukt, return code {rc}\n")

# Deze functie wordt uitgevoerd wanneer een bericht op het topic binnenkomt
def on_message(client, userdata, msg):
    # De payload (het bericht) is in bytes, dus we decoderen het naar een string
    # We maken er direct hoofdletters van om "on", "On", "ON" etc. te accepteren
    payload = msg.payload.decode("utf-8").upper() 
    print(f"Bericht ontvangen op topic '{msg.topic}': {payload}")

    if payload == "ON":
        relais.on()
        print(f"[ACTIE] Device op pin {GPIO_PIN} AANgeschakeld")
    elif payload == "OFF":
        relais.off()
        print(f"[ACTIE] Device op pin {GPIO_PIN} UITgeschakeld")
    else:
        print(f"[WAARSCHUWING] Onbekend commando ontvangen: '{payload}'. Negeer.")

# --- Hoofdprogramma ---
# Maak een MQTT client instance aan met de nieuwste callback API versie
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Wijs de callback functies toe
client.on_connect = on_connect
client.on_message = on_message

# Probeer te verbinden met de broker en vang veelvoorkomende fouten op
try:
    print("Verbinding maken met MQTT Broker...")
    client.connect(MQTT_BROKER_ADRES)
except ConnectionRefusedError:
    print("!!! VERBINDING GEWEIGERD. Draait de Mosquitto service wel? (sudo systemctl status mosquitto)")
    exit()
except OSError:
    print("!!! NETWERKFOUT. Is het broker adres correct en is het netwerk bereikbaar?")
    exit()

# Start de 'loop'. Dit is een blokkerende functie die continu luistert naar berichten
# en de verbinding automatisch herstelt.
client.loop_forever()
