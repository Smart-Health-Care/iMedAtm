import time

import RPi.GPIO as GPIO


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.IN)

IR_PIN = 16
LDR_PIN = 32
motora = 24
motorb = 33
VACUUM_P = 22
VACUUM_N = 23
MINI_STEPPER_coil_A1 = 35
MINI_STEPPER_coil_A2 = 36
MINI_STEPPER_coil_B1 = 37
MINI_STEPPER_coil_B2 = 38
DIR_CHAMBER = 15
STEP_CHAMBER = 13
DIR_ROLLER = 11
STEP_ROLLER = 7
LASER = 21
DELAY = .005


def set2():
    GPIO.setup(MINI_STEPPER_coil_A1, GPIO.OUT)
    GPIO.setup(MINI_STEPPER_coil_A2, GPIO.OUT)
    GPIO.setup(MINI_STEPPER_coil_B1, GPIO.OUT)
    GPIO.setup(MINI_STEPPER_coil_B2, GPIO.OUT)

def setStep(w1, w2, w3, w4):
    GPIO.output(MINI_STEPPER_coil_A1, w1)
    GPIO.output(MINI_STEPPER_coil_A2, w2)
    GPIO.output(MINI_STEPPER_coil_B1, w3)
    GPIO.output(MINI_STEPPER_coil_B2, w4)

def set1():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(VACUUM_P, GPIO.OUT)
    GPIO.setup(VACUUM_N, GPIO.OUT)
    GPIO.setwarnings(False)

def vacuum_on():
    set1()
    GPIO.output(VACUUM_P, GPIO.LOW)
    GPIO.output(VACUUM_N, GPIO.HIGH)

def vacuum_off():
    set1()
    GPIO.output(VACUUM_P, GPIO.LOW)
    GPIO.output(VACUUM_N, GPIO.LOW)

def shake():
    set2()
    delay = 0.003
    steps = 20
    for i in range(0, 200):
        forward_vacuum_arm(20, delay)
        backward_vacuum_arm(20, delay)

def forward_vacuum_arm(steps, delay=0.003):
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

def backward_vacuum_arm(steps, delay=0.003):
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

def setpins_chamber():
    GPIO.setup(DIR_CHAMBER, GPIO.OUT)
    GPIO.setup(STEP_CHAMBER, GPIO.OUT)

def setpins_roller():
    GPIO.setup(DIR_ROLLER, GPIO.OUT)
    GPIO.setup(STEP_ROLLER, GPIO.OUT)

def forward_chamber_vacuum(step_count):
    setpins_chamber()
    GPIO.output(DIR_CHAMBER, 0)
    for x in range(step_count):
        GPIO.output(STEP_CHAMBER, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_CHAMBER, GPIO.LOW)
        time.sleep(DELAY)

def backward_chamber_vacuum(step_count):
    setpins_chamber()
    GPIO.output(DIR_CHAMBER, 1)
    for x in range(step_count):
        GPIO.output(STEP_CHAMBER, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_CHAMBER, GPIO.LOW)
        time.sleep(DELAY)

def set():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(motora, GPIO.OUT)
    GPIO.setup(motorb, GPIO.OUT)
    GPIO.setwarnings(False)

def backward():
    set()
    GPIO.output(motora, GPIO.HIGH)
    GPIO.output(motorb, GPIO.LOW)

def forward():
    set()
    GPIO.output(motora, GPIO.LOW)
    GPIO.output(motorb, GPIO.HIGH)

def stop():
    set()
    GPIO.output(motora, GPIO.LOW)
    GPIO.output(motorb, GPIO.LOW)

def rc_time():
    count = 0
    GPIO.setup(LDR_PIN, GPIO.OUT)
    GPIO.output(LDR_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(LDR_PIN, GPIO.IN)
    while (GPIO.input(LDR_PIN) == GPIO.LOW):
        count += 1

    return count

def laser_on():
    GPIO.setup(LASER, GPIO.OUT)
    GPIO.output(LASER, GPIO.HIGH)

def laser_off():
    GPIO.setup(LASER, GPIO.OUT)
    GPIO.output(LASER, GPIO.LOW)

def laser_calibrate():
    laser_on()
    threshold = 0
    for i in range(0, 5):
        threshold = (threshold + rc_time()) / 2
    laser_off()
    return threshold

def rotate_chamber(chamber_number):
    GPIO.setmode(GPIO.BOARD)
    laser_flag = False
    delay = 0.003
    # Chamber Movement
    chamber_steps = 0
    n = 395
    if chamber_number == 1:
        chamber_steps = n
        forward_chamber_vacuum(chamber_steps)
    elif chamber_number == 2:
        chamber_steps = n * 2
        forward_chamber_vacuum(chamber_steps)
    elif chamber_number == 3:
        chamber_steps = n * 3
        forward_chamber_vacuum(chamber_steps)
        # backward_chamber_vacuum(chamber_steps)
    # Vacuum Arm movement
    threshold = laser_calibrate()
    chamber_steps = n * 4 - chamber_steps
    GPIO.setup(IR_PIN, GPIO.IN)
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
        ir = GPIO.input(IR_PIN)
        count += 1
        print(count)
        if ir == 0:
            vacuum_on()
            time.sleep(5)
            backward_vacuum_arm(count)
            time.sleep(3)
            # laser_on()
            # for i in range(0, 3):
            #     S = rc_time()
            #     if S > threshold:
            #         laser_flag = True
            #     time.sleep(1)
            # laser_off()
            # if laser_flag:
            #     print("medicine not picked")
            #     vacuum_off()
            #     continue
            # else:
            print("medicine picked ")
            forward_chamber_vacuum(chamber_steps)
            # backward_chamber_vacuum(chamber_steps)
            time.sleep(1)
            vacuum_off()
            break
    GPIO.cleanup()

def rotate_spring():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IR_PIN, GPIO.IN)
    flag = True
    while True:
        if flag:
            flag = False
            forward()
            time.sleep(0.5)
        i = GPIO.input(IR_PIN)
        if i == 0:
            stop()
            time.sleep(0.03)
            break
        else:
            forward()
            time.sleep(0.03)
    GPIO.cleanup()


def rotate_wheel():
    GPIO.setmode(GPIO.BOARD)
    step_count = 200
    setpins_roller()
    GPIO.output(DIR_ROLLER, 0)
    for x in range(step_count):
        GPIO.output(STEP_ROLLER, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_ROLLER, GPIO.LOW)
        time.sleep(DELAY)
    GPIO.cleanup()
