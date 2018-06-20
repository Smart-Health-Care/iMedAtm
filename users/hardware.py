import time

import RPi.GPIO as GPIO
import serial

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# spring pins


IR_PIN1 = 31
IR_PIN2 = 29
# IR_PIN3 =  21
# IR_PIN4 = 22
motora = 11
motorb = 12
# motorc =
# motord =
# motore =
# motorf =
# roller pin declaration
DIR_ROLLER = 18
STEP_ROLLER = 16

# vacuum motors
DELAY = 0.005
DIR_CHAMBER = 21  # 29# Direction GPIO Pin
STEP_CHAMBER = 19  # 31
VACUUM_P = 24
# VACUUM_N = 19
# IR_PIN5 =
MINI_STEPPER_coil_A1 = 35
MINI_STEPPER_coil_A2 = 36
MINI_STEPPER_coil_B1 = 37
MINI_STEPPER_coil_B2 = 38
# LDR_PIN = 29
# LASER = 40
PROXI = 33


# spring motor functions

def set():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(motora, GPIO.OUT)
    GPIO.setup(motorb, GPIO.OUT)
    # GPIO.setup(motorc, GPIO.OUT)
    # GPIO.setup(motord, GPIO.OUT)
    GPIO.setwarnings(False)


def ir_spring1():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IR_PIN1, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    i = GPIO.input(IR_PIN1)
    return (i)


def proximity():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PROXI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    k = GPIO.input(PROXI)
    return (k)


def ir_spring2():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IR_PIN2, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    j = GPIO.input(IR_PIN2)
    return (j)


def forward1():
    set()
    GPIO.output(motora, GPIO.HIGH)


def stop1():
    set()
    GPIO.output(motora, GPIO.LOW)


def forward2():
    set()
    GPIO.output(motorb, GPIO.HIGH)


def stop2():
    set()
    GPIO.output(motorb, GPIO.LOW)


# roller functions


def setpins_roller():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DIR_ROLLER, GPIO.OUT)
    GPIO.setup(STEP_ROLLER, GPIO.OUT)


def forward_roller(step_count=25):
    GPIO.setmode(GPIO.BOARD)
    setpins_roller()
    delay = 0.005
    GPIO.output(DIR_ROLLER, GPIO.LOW)
    for x in range(step_count):
        GPIO.output(STEP_ROLLER, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_ROLLER, GPIO.LOW)
        time.sleep(delay)
    # GPIO.cleanup()


def backward_roller(step_count=25):
    GPIO.setmode(GPIO.BOARD)
    setpins_roller()
    delay = 0.005
    GPIO.output(DIR_ROLLER, GPIO.HIGH)
    for x in range(step_count):
        GPIO.output(STEP_ROLLER, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_ROLLER, GPIO.LOW)
        time.sleep(delay)
    # GPIO.cleanup()


# vacuum functions

def set1():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(VACUUM_P, GPIO.OUT)
    # GPIO.setup(VACUUM_N, GPIO.OUT)
    GPIO.setwarnings(False)


def set2():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(MINI_STEPPER_coil_A1, GPIO.OUT)
    GPIO.setup(MINI_STEPPER_coil_A2, GPIO.OUT)
    GPIO.setup(MINI_STEPPER_coil_B1, GPIO.OUT)
    GPIO.setup(MINI_STEPPER_coil_B2, GPIO.OUT)


def setStep(w1, w2, w3, w4):
    GPIO.setmode(GPIO.BOARD)
    GPIO.output(MINI_STEPPER_coil_A1, w1)
    GPIO.output(MINI_STEPPER_coil_A2, w2)
    GPIO.output(MINI_STEPPER_coil_B1, w3)
    GPIO.output(MINI_STEPPER_coil_B2, w4)


def vacuum_on():
    set1()
    GPIO.output(VACUUM_P, GPIO.HIGH)
    # GPIO.output(VACUUM_N, GPIO.LOW)


def vacuum_off():
    set1()
    GPIO.output(VACUUM_P, GPIO.LOW)
    # GPIO.output(VACUUM_N, GPIO.LOW)


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
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DIR_CHAMBER, GPIO.OUT)
    GPIO.setup(STEP_CHAMBER, GPIO.OUT)


def backward_chamber_vacuum(step_count=33):
    setpins_chamber()
    DELAY = 0.005
    GPIO.output(DIR_CHAMBER, 0)
    for x in range(step_count):
        GPIO.output(STEP_CHAMBER, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_CHAMBER, GPIO.LOW)
        time.sleep(DELAY)


def forward_chamber_vacuum(step_count=33):
    setpins_chamber()
    DELAY = 0.005
    GPIO.output(DIR_CHAMBER, 1)
    for x in range(step_count):
        GPIO.output(STEP_CHAMBER, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_CHAMBER, GPIO.LOW)
        time.sleep(DELAY)


# def rc_time():
#     count = 0
#     GPIO.setup(LDR_PIN, GPIO.OUT)
#     GPIO.output(LDR_PIN, GPIO.LOW)
#     time.sleep(0.1)
#     GPIO.setup(LDR_PIN, GPIO.IN)
#     while (GPIO.input(LDR_PIN) == GPIO.LOW):
#         count += 1
#
#     return count

def current_vacuum():
    port = 0
    ser = serial.Serial(
        port='/dev/ttyUSB' + str(port),
        baudrate=9600,
    )
    x = ser.readline()
    x = x.replace("\r", "").replace("\n", "")
    return (x)


# def laser_on():
#     GPIO.setup(LASER, GPIO.OUT)
#     GPIO.output(LASER, GPIO.HIGH)
#
#
# def laser_off():
#     GPIO.setup(LASER, GPIO.OUT)
#     GPIO.output(LASER, GPIO.LOW)


# def laser_calibrate():
#     laser_on()
#     threshold = 0
#     for i in range(0, 5):
#         threshold = (threshold + rc_time()) / 2
#     laser_off()
#     return threshold


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
    # threshold = laser_calibrate()
    chamber_steps = n * 4 - chamber_steps
    GPIO.setup(PROXI, GPIO.IN)
    set2()
    count = 0
    while True:
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        count += 1
        print(count)
        ir = GPIO.input(PROXI)

        if ir == 0:
            backward_vacuum_arm(20)
            count += 20
            vacuum_on()
            time.sleep(5)
            forward_vacuum_arm(count)
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
    # GPIO.cleanup()


def rotate_spring1():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IR_PIN1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    flag = True
    while True:
        if flag:
            flag = False
            forward1()
            time.sleep(0.5)
        i = GPIO.input(IR_PIN1)
        if i == 0:
            stop1()
            time.sleep(0.03)
            break
        else:
            forward1()
            time.sleep(0.03)
    # GPIO.cleanup()


def rotate_spring2():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IR_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    flag = True
    while True:
        if flag:
            flag = False
            forward2()
            time.sleep(0.5)
        k = GPIO.input(IR_PIN2)
        if k == 0:
            stop2()
            time.sleep(0.03)
            break
        else:
            forward2()
            time.sleep(0.03)
    # GPIO.cleanup()


def rotate_wheel():
    GPIO.setmode(GPIO.BOARD)
    DELAY = 0.003
    step_count = 200
    setpins_roller()
    GPIO.output(DIR_ROLLER, 0)
    for x in range(step_count):
        GPIO.output(STEP_ROLLER, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_ROLLER, GPIO.LOW)
        time.sleep(DELAY)
    # GPIO.cleanup()


# def vacuum_complete():
#     forward_chamber_vacuum(800)
#     vacuum_on()
#     forward_vacuum_arm(460)
#     time.sleep(1)
#     backward_vacuum_arm(545)
#     laser_on()
#     proximity()
#     laser_calibrate()
#     forward_chamber_vacuum(800)
#     vacuum_off()


def shake():
    set2()
    steps = 20
    for i in range(0, 5):
        forward_chamber_vacuum(steps)
        backward_chamber_vacuum(steps)
