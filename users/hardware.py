import time

import RPi.GPIO as GPIO

# Wheel Control
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)

GPIO.setup(40, GPIO.IN)

motora = 7
motorb = 8  # Input Pin
motorc = 5  # Enable Pin

# chamber control
GPIO.setmode(GPIO.BOARD)
GPIO.setup(38, GPIO.IN)

motord = 16
motore = 18  # Input Pin
motorf = 19

coil_A1 = 13
coil_A2 = 11
coil_B1 = 15
coil_B2 = 12

coil_1 = 21
coil_2 = 22
coil_3 = 23
coil_4 = 24


laser = 21

def set2():
    GPIO.setup(coil_A1, GPIO.OUT)
    GPIO.setup(coil_A2, GPIO.OUT)
    GPIO.setup(coil_B1, GPIO.OUT)
    GPIO.setup(coil_B2, GPIO.OUT)


def set3():
    GPIO.setup(coil_1, GPIO.OUT)
    GPIO.setup(coil_2, GPIO.OUT)
    GPIO.setup(coil_3, GPIO.OUT)
    GPIO.setup(coil_4, GPIO.OUT)


def setStep1(w5, w6, w7, w8):
    GPIO.output(coil_1, w5)
    GPIO.output(coil_2, w6)
    GPIO.output(coil_3, w7)
    GPIO.output(coil_4, w8)


def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A1, w1)
    GPIO.output(coil_A2, w2)
    GPIO.output(coil_B1, w3)
    GPIO.output(coil_B2, w4)


def set1():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(motord, GPIO.OUT)
    GPIO.setup(motore, GPIO.OUT)
    GPIO.setup(motorf, GPIO.OUT)
    GPIO.setwarnings(False)


def vacuum_on():
    set1()
    GPIO.output(motord, GPIO.LOW)
    GPIO.output(motore, GPIO.HIGH)
    GPIO.output(motorf, GPIO.HIGH)


def vacuum_off():
    set1()
    GPIO.output(motorf, GPIO.LOW)


def forward_vaccum_arm(delay, steps):
    set2()
    for i in range(0, steps):
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)


def backward_vaccum_arm(delay, steps):
    set2()
    for i in range(0, steps):
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(1, 0, 1, 0)
        time.sleep(delay)


DIR_CHAMBER = 15  # Direction GPIO Pin
STEP_CHAMBER = 16

DIR_ROLLER = 12
STEP_ROLLER = 13  # Step GPIO Pin


# Steps per Revolution (360 / 0.067 * 3.5)


def setpins_chamber():
    GPIO.setup(DIR_CHAMBER, GPIO.OUT)
    GPIO.setup(STEP_CHAMBER, GPIO.OUT)


def setpins_roller():
    GPIO.setup(DIR_ROLLER, GPIO.OUT)
    GPIO.setup(STEP_ROLLER, GPIO.OUT)


delay = .005


def forward_chamber_vacuum(step_count):
    setpins_chamber()
    GPIO.output(DIR_CHAMBER,GPIO.LOW)
    for x in range(step_count):
        GPIO.output(STEP_CHAMBER, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_CHAMBER, GPIO.LOW)
        time.sleep(delay)


def backward_chamber_vacuum(step_count):
    setpins_chamber()
    GPIO.output(DIR_CHAMBER, 1)
    for x in range(step_count):
        GPIO.output(STEP_CHAMBER, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_CHAMBER, GPIO.LOW)
        time.sleep(delay)


# Wheel Control
def set():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(motora, GPIO.OUT)
    GPIO.setup(motorb, GPIO.OUT)
    GPIO.setup(motorc, GPIO.OUT)
    GPIO.setwarnings(False)


def backward():
    set()
    GPIO.output(motora, GPIO.HIGH)
    GPIO.output(motorb, GPIO.LOW)
    GPIO.output(motorc, GPIO.HIGH)


def forward():
    set()
    GPIO.output(motora, GPIO.LOW)
    GPIO.output(motorb, GPIO.HIGH)
    GPIO.output(motorc, GPIO.HIGH)


def stop():
    set()
    GPIO.output(motorc, GPIO.LOW)


def rc_time(pin_to_circuit):
    count = 0
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(pin_to_circuit, GPIO.IN)
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1

    return count


def laser_on():
    GPIO.setup(laser, GPIO.OUT)
    GPIO.output(laser, GPIO.HIGH)


def laser_off():
    GPIO.setup(laser, GPIO.OUT)
    GPIO.output(laser, GPIO.LOW)


def rotate_chamber(chamber_number):
    laser_flag = False
    delay = 0.003
    # Chamber Movement
    chamber_steps = 0
    n = 50
    if chamber_number == 1:
        chamber_steps = n
    elif chamber_number == 2:
        chamber_steps = n * 2
    elif chamber_number == 3:
        chamber_steps = n * 3
    forward_chamber_vacuum(chamber_steps)
    # Vacuum Arm movement
    set2()
    count = 0
    while True:
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        ir = GPIO.input(40)
        count += 1
        if ir == 0:
            vacuum_on()
            time.sleep(5)
            backward_vaccum_arm(delay, count)
            laser_on()
            for i in range(0, 5):
                S = rc_time(38)
                if S > 10000:
                    laser_flag = True
                time.sleep(3)
            laser_off()
            if laser_flag:
                print("medicine not picked")
                vacuum_off()
                continue
            else:
                print("medicine picked ")
                backward_chamber_vacuum(chamber_steps)
                time.sleep(1)
                vacuum_off()
                break


def rotate_spring():
    flag = True
    while True:
        if flag:
            flag = False
            forward()
            time.sleep(0.5)
        i = GPIO.input(3)
        if i == 0:
            flag = True
            stop()
            time.sleep(0.5)
        else:
            forward()
            time.sleep(0.5)
