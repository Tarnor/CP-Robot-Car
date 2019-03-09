# CircuitPython Automated Car Playground
# Version 0.0 Update Libraries/CircuitPython
# Version 0.1 Pre-Car Connection testing


# Functionality to Model
# Car Going Forward/Backward/Turning/Stopping
# Control of Speed
# Bluetooth Control of Car via UART serial
# Autonomous Driving via Line Tracking
# Autonomous Driving via Object Avoidance
'''
Remote Codes:
S, F, T	Speed Up, Forward, Timestamp
L, H, R	Left, Halt(Stop), Right
D, B, Y	Speed Down, Reverse(Backup), Horn Honk
1, 2, 3	Line Tracking, BT Remote, Obstical Avoidance
Q, W, E	Servo Left, Measure Distance, Servo Right
4, 5, 6	Temp, Humidity, Pressure
7, 8, 9	G-Force, Magnet, Gyro
​
Analog/Digital Pins for Elegoo Shield
A0	free Horn?
A1	free
A2	free
A3	free
A4	Echo Ultrasonic Sensor
A5	Trigger Ultrasonic Sensor
D0	RX Bluetooth
D1	TX Bluetooth
D2	Line Tracking Left
D3	SG90 Servo for Ultrasonic Sensor
D4	Line Tracking Middle
D5	ENA (Speed Right Side A)
D6	ENB (Speed Left Side B)
D7	Motor Left
D8	Motor Left
D9	Motor Right
D10	Line Tracking Right
D11	Motor Right
D12	IR Receiver
D13	Unused (NeoPixel on Lauren's Board)
I2C	free for I2C Sensors/Display?
​
'''
# Libraries Needed:------------------------------------------------------------:
import board
import busio
import digitalio
import time
import neopixel
import simpleio
import adafruit_sdcard
import microcontroller
import storage
import os

# Set up Objects--------------------------------------------------------------:
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness = 0.2, auto_write=True)
uart = busio.UART(board.TX, board.RX, baudrate=9600)
# SD Card Objects
spi = busio.SPI(board.SD_SCK, board.SD_MOSI, board.SD_MISO)
cs = digitalio.DigitalInOut(board.SD_CS)
sdcard = adafruit_sdcard.SDCard(spi,cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")


# Colors
RED = (50, 0, 0)
YELLOW = (50, 30, 0)
GREEN = (0, 50, 0)
CYAN = (0, 50, 50)
BLUE = (0, 0, 50)
PURPLE = (40, 0, 50)
WHITE = (50,50,50)
BYELLOW = (100,60,0)


# Movement routines:--------------------------------------------------------:
def move(direction):
    if direction == "F":
        # Forward
        pixels[0] = (GREEN)
        log_action("Forward", 0)
    elif direction == "B":
        # Reverse
        pixels[0] = YELLOW
        log_action("Backup", 0)
    elif direction == "L":
        # Turn Left
        pixels[0] = BLUE
        log_action("Turn Left", 0)
    elif direction == "R":
        # Turn Right
        pixels[0] = PURPLE
        log_action("Turn Right", 0)
    elif direction == "H":
        # Stop
        pixels[0] = RED
        log_action("Halt", 0)
    else:
        pass

# Speed Routines:-----------------------------------------------------------:
def increase_speed(car_speed):
    #Routine which will increase the speed
    car_speed = car_speed + 10
    if car_speed >200:
        car_speed = 200
    log_action("Speed UP to", car_speed)
    return car_speed

def decrease_speed(car_speed):
    #Routine which will decrease the speed
    car_speed = car_speed - 10
    if car_speed <40:
        car_speed = 40
    log_action("Speed DN to", car_speed)
    return car_speed

# Autonomous Driving Routines:----------------------------------------------:
def line_tracking():
    # Routine where car follows a black line
    pixels[0] = WHITE
    log_action("Line Tracking", 1)
    while True:
        data = uart.read(1)  # read up to 32 bytes
        # Line Tracking Control Routine Here
        if data is not None:
            # convert bytearray to string
            data_string = ''.join([chr(b) for b in data])
            print(data_string, end="")
            #print(data)
            if data_string == 'T':
                log_action("Timestamp", time.monotonic())
            elif data_string == '2': # Return to Bluetooth Remote
                log_action("BT Remote", 0)
                move("H") # Stop the car first
                return


def obsticle_avoidance():
    # Routine where car is automated to obsticle avoidance routine
    # can be made more complicated than Arduino equivilent
    pixels[0] = BYELLOW
    log_action("Obsticle Avoidance", 2)
    while True:
        data = uart.read(1)  # read up to 32 bytes
        # Obsticle Avoidance Routine Here
        if data is not None:
            # convert bytearray to string
            data_string = ''.join([chr(b) for b in data])
            print(data_string, end="")
            #print(data)
            if data_string == 'T':
                log_action("Timestamp", time.monotonic())
            elif data_string == '2': # Return to Bluetooth Remote
                log_action("BT Remote", 0)
                move("H") # Stop the car first
                return

# Control Ultrasonic Sensor & Servo Motors to Move and Measure---------------:

def pan_left(servo_angle):
    servo_angle = servo_angle - 10
    if servo_angle < 10:
        servo_angle = 10
    log_action("Pan Left to", servo_angle)
    return servo_angle

def measure_distance():
    measure_dist = 20.0 #temporary until working
    log_action("Distance to object is", measure_dist)
    return measure_dist

def pan_right(servo_angle):
    servo_angle = servo_angle + 10
    if servo_angle > 170:
        servo_angle = 170
    log_action("Pan Right to", servo_angle)
    return servo_angle 
    
def honk():
    log_action("Honk!", 0)
    #simpleio.tone(board.A0, 440, duration=0.25)


# This routine outputs feedback to Serial Monitor, Bluetooth and SD Card Log File
def log_action(message, value):
    print(">"+message + " " + str(value))
    uart.write(str.encode(str(time.monotonic())+" "+message+" "+str(value)+"\n"))
    with open(log_fn, "a") as sdfile:
        sdfile.write(str.encode(str(time.monotonic())+" "+message+" "+str(value)+"\n"))
    return

# Set Defaults for when car first boots-----------------------------------------:

# Write to New Logfile
i=0
log_fn = "log" + str(int(i)) +".txt"
while log_fn in os.listdir("/sd"):
    i +=1
    log_fn = "log" + str(int(i)) +".txt"
log_fn = "/sd/" + log_fn
print("Log file name: " + log_fn)

move("H")           #Start the car Halted
car_speed = 100     #starting speed of car is 100
servo_angle = 90    #start servo facing front

# Loop Starts Here ------------------------------------------------------------:
while True:
    data = uart.read(1)  # read up to 32 bytes
    if data is not None:
        # convert bytearray to string
        data_string = ''.join([chr(b) for b in data])
        print(data_string, end="")
        #print(data)
        if data_string == 'T':
            log_action("Timestamp", time.monotonic())
        elif data_string == 'F': # Forward
            move("F")
        elif data_string == 'B': # Backup
            move("B")
        elif data_string == 'L': # Turn Left
            move("L")
        elif data_string == 'R': # Turn Right
            move("R")
        elif data_string == 'H': # Halt the car
            move("H")
        elif data_string == 'S': # Speed Up car
            car_speed = increase_speed(car_speed)
        elif data_string == 'D': # Speed Down car
            car_speed = decrease_speed(car_speed)
        elif data_string == '1': # Start Line Tracking
            line_tracking()
        elif data_string == '3': # Start Obsticle avoidance
            obsticle_avoidance()
        elif data_string == 'Y': # Honk the horn
            honk()
        elif data_string == 'Q': # Pan Distance Sensor Left
            servo_angle = pan_left(servo_angle)
        elif data_string == 'W': # Measure Ultrasonic Distance
            measure_dist = measure_distance()
        elif data_string == 'E': # Pan Distance Sensor Right
            servo_angle = pan_right(servo_angle)
        elif data_string == 'Z': # Pan Distance Sensor Right
            log_action("My battery is low and it%cs getting dark." % 39, 0)
        # Flash LED on Keypress just to show something happening
        led.value = not led.value

# End of Program --------------------------------------------------------------