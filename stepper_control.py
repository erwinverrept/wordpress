#CONTROL_PINS = [17, 18, 27, 22]

import RPi.GPIO as GPIO
import time
import sys

# Definieer de GPIO-pinnen voor de stappenmotor
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22

# Setup van de GPIO
GPIO.setmode(GPIO.BCM)
pins = [IN1, IN2, IN3, IN4]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Definieer de stappensequentie (half-step voor meer precisie)
# 8 stappen per cyclus
seq = [[1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1],
       [1,0,0,1]]

def rotate_degrees(degrees):
    """
    Draait de motor een bepaald aantal graden.
    Positieve graden = met de klok mee.
    Negatieve graden = tegen de klok in.
    """
    # De 28BYJ-48 motor heeft 512 stappen per volledige rotatie in full-step mode.
    # In half-step mode (8 stappen per cyclus), zijn er 512 * (8/4) = 1024 * 4 = 4096 stappen per rotatie.
    # Stappen per graad: 4096 / 360 ≈ 11.377
    steps_per_degree = 4096 / 360
    total_steps = int(abs(degrees) * steps_per_degree)

    step_dir = 1 if degrees > 0 else -1 # 1 voor met de klok mee, -1 voor tegen de klok in

    step_counter = 0
    for _ in range(total_steps):
        for pin in range(4):
            GPIO.output(pins[pin], seq[step_counter][pin])
        step_counter += step_dir

        # Als we het einde van de sequence bereiken, begin opnieuw
        if step_counter >= len(seq):
            step_counter = 0
        if step_counter < 0:
            step_counter = len(seq) - 1

        time.sleep(0.001) # Wachttijd tussen stappen, pas aan voor snelheid

if __name__ == "__main__":
    try:
        # Lees het aantal graden van de command-line argumenten
        if len(sys.argv) > 1:
            degrees_to_rotate = float(sys.argv[1])
            print(f"Draaien: {degrees_to_rotate} graden...")
            rotate_degrees(degrees_to_rotate)
            print("Klaar.")
        else:
            print("Geef het aantal graden op als argument. Bv: python3 stepper_control.py 90")

    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")
    finally:
        # Ruim de GPIO-pinnen op
        GPIO.cleanup()