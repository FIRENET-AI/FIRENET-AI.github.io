import machine
import time

relay_pin = machine.Pin(15, machine.Pin.OUT)


ON_TIME = 2.5 * 60   
OFF_TIME = 15 * 60 

print("Starting Pico...")

while True:
    print("Relay ON")
    relay_pin.value(1)
    time.sleep(ON_TIME)
    
    print("Relay OFF")
    relay_pin.value(0)
    time.sleep(OFF_TIME)
