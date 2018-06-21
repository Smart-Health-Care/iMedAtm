# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, timedelta
from random import randint

import cv2
import pytz
import pyzbar.pyzbar as pyzbar
import requests
from bluetooth import *
from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime

# from hardware import *
# Create your views here.
from iMedAtm import settings
from iMedAtm.settings import SERVER_URL
from messageotp import send_message
# from printer_check import print_prescription

CHAMBER_1_STEPS = 400
CHAMBER_2_STEPS = 800
DELAY = 0.03


def decode(im):
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    # Print results
    for obj in decodedObjects:
        if obj.type == 'QRCODE':
            return obj.data


def QRScanner():
    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        # cv2.namedWindow("QR", cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty("QR", cv2.WND_PROP_FULLSCREEN, 1)
        # cv2.imshow("QR", img)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        data = decode(img)
        if data:
            # cv2.destroyAllWindows()
            # cap.release()
            # cv2.waitKey(1)

            return data


def CameraAccess(request):
    data = QRScanner()
    # keyboard.send("alt+tab")
    # keyboard.send("enter")
    if "vendor" in data:
        request.session.__setitem__("vendor_id", data.split("-")[1])
        return redirect('vendor_load')
    else:
        request.session.__setitem__('aadhar_number', data)

        otp = randint(1000, 9999)
        response = requests.get(SERVER_URL + "/api/v1/user_details?aadhar_number=" + str(data))
        number = response.json().get("mobile_number")
        send_message("Your OTP for iMedDispenser is " + str(otp), str(number))
        request.session.__setitem__("otp", otp)
        return redirect('otp_enter')
    # time.sleep(10)
    # return redirect('verify_details')


def display_camera(request):
    return render(request, 'admin_theme/scan_camera.html')


def landing_page(request):
    return render(request, 'admin_theme/scan_camera.html')


# def dashboard(request):
#     return render(request, 'admin_theme/dashboard.html')


def otp_enter(request):
    aadhar = request.session.__getitem__('aadhar_number')
    if not aadhar:
        return redirect('landing_page')
    if request.method == 'POST':
        otp = int(request.POST.get("otp"))
        # response = requests.post(SERVER_URL + "/api/v1/authenticate", {'aadhar': aadhar, 'otp': otp})
        otp_sess = int(request.session.__getitem__("otp"))
        if otp == otp_sess:
            response = requests.get(SERVER_URL + "/api/v1/user_details?aadhar_number=" + str(aadhar))
            request.session.__setitem__('user', response.json())
            return redirect('prescription_list')
        else:
            messages.error(request, "Wrong Credentials")
    return render(request, 'admin_theme/otp_enter_page.html')


def verify_details(request):
    aadhar = request.session.__getitem__('aadhar_number')
    if not aadhar:
        return redirect('landing_page')
    data = request.session.__getitem__('user')
    return render(request, 'admin_theme/verify_details.html', {'data': data, 'aadhar': aadhar})


def prescription_list(request):
    aadhar = request.session.__getitem__('aadhar_number')
    if not aadhar:
        return redirect('landing_page')
    response = requests.get(SERVER_URL + "/api/v1/user_prescription?aadhar_number=" + aadhar)
    data = None
    if response.status_code == 200:
        request.session.__setitem__("prescription_data", response.json())
        received_data = response.json()
        data = []
        for prescription in received_data:
            doctor = prescription.get("doctor")
            created = prescription.get("created_at")
            doc_name = doctor.get("first_name") + " " + doctor.get("last_name")
            doc_pic = None
            if doctor.get("profile_pic"):
                doc_pic = SERVER_URL + doctor.get("profile_pic")
            id = prescription.get("id")
            created = parse_datetime(created).strftime("%d/%m/%Y %H:%M")
            data.append({
                'doc_name': doc_name,
                'id': id,
                'created': created,
                'doc_pic': doc_pic
            })
    return render(request, 'admin_theme/prescription_list.html', {'datas': data})


def prescription_view(request, id):
    response = requests.get(SERVER_URL + "/api/v1/prescription?id=" + id + "&device_id=" + str(settings.DEVICE_ID))
    prescription_data = request.session.__getitem__("prescription_data")
    request.session.__setitem__("prescription_id", id)
    if not prescription_data:
        return redirect('landing_page')
    doctor = None
    for data in prescription_data:
        data_id = int(data.get('id'))
        if data_id == int(id):
            doctor = data.get("doctor")
            break
    data = response.json()
    if data.get("status"):
        return redirect("prescription_list")
    request.session.__setitem__("chamber_data", data.get("chamber_data"))
    request.session.__setitem__("dispense_details", data.get("prescription_data"))
    request.session.__setitem__("medicines", data.get("medicines"))
    data = data.get("prescription_data")
    request.session.__setitem__("medicine_qty", data)
    return render(request, 'admin_theme/prescription_view.html',
                  {'datas': data, 'doctor': doctor, 'prescription_id': int(id)})


def payment_confirmation(request):
    if request.method == 'POST':
        post_data = request.POST
        request.session.__setitem__("post_data", post_data)
        prescription_id = request.POST.get("prescription_id")
        medicine_data_1 = request.session.__getitem__("dispense_details")
        for datas in medicine_data_1:
            qty = request.POST.get(datas.get("medicine"))
            if qty:
                qty = int(qty)
                if qty > int(datas.get("max_dispensable_qty")):
                    messages.error(request, datas.get("medicine") + " quantity should be less than " + str(datas.get(
                        "max_dispensable_qty")))
                    return redirect("prescription_view", prescription_id)
        total = 0
        for datas in medicine_data_1:
            qty = request.POST.get(datas.get("medicine"))
            if qty:
                qty = int(qty)
                price = float(datas.get("medicine_amount"))
                total += price * qty
        return render(request, 'admin_theme/payment_confirm.html', {"total": int(total)})
    return HttpResponse("Wrong Request")


def payment(request, total):
    aadhar = request.session.__getitem__('aadhar_number')
    data = request.session.__getitem__('user')
    response = requests.post(SERVER_URL + "/users/api/v1/initialize_payment",
                             data={'user_id': data.get("id"), 'aadhar': aadhar, 'amount': total})
    if response.status_code == 200:
        payment_request_id = response.json().get("id")
        return redirect('payment_wait', payment_request_id)
    else:
        messages.error(request, "Error Processing Payment")
        # return redirect('end_session')


def payment_wait(request, payment_request_id):
    date = datetime.now() + timedelta(minutes=5)
    asia = pytz.timezone("Asia/Kolkata")
    date_string = pytz.utc.localize(date).astimezone(asia).strftime("%a %b %d %Y %H:%M:%S GMT %z")
    check_payment_url = SERVER_URL + "/users/api/v1/check_payment?payment_request_id=" + payment_request_id
    return render(request, 'admin_theme/payment_wait.html',
                  {'check_url': check_payment_url, "date_string": date_string})


chamber = 0
ROLLER_STEP_COUNT = 50

#
# def spring_1_dispense(count):
#     while count != 0:
#         rotate_spring1()
#         time.sleep(1)
#         count -= 1
#
#
# def spring_2_dispense(count):
#     while count != 0:
#         rotate_spring2()
#         count -= 1
#
#
# def roller_right_dispense(count):
#     while count != 0:
#         backward_roller(13)
#         time.sleep(1)
#         count -= 1
#
#
# def roller_left_dispense(count):
#     while count != 0:
#         forward_roller(13)
#         time.sleep(1)
#         count -= 1
#
#
# def vacuum(chamber):
#     temp = chamber
#     while temp > 0:
#         forward_chamber_vacuum()
#         temp -= 1
#     total_steps = 0
#     delay = 0.003
#     max_steps = 1900
#     # flag = True
#     while total_steps < max_steps:
#         i = proximity()
#         if i == 0:
#             set3()
#             arm_down(500)
#             total_steps += 500
#             vacuum_on()
#             time.sleep(2)
#             arm_up(total_steps)
#             # i = proximity()
#             # if i != 0:
#             #     # if flag:
#             #     #     flag = False
#             #     continue
#
#             temp = 6 - chamber
#             while temp > 0:
#                 forward_chamber_vacuum()
#                 temp -= 1
#             vacuum_off()
#             break
#         else:
#             GPIO.setmode(GPIO.BOARD)
#             set3()
#             delay = 0.001
#             GPIO.output(ARM_DIR, GPIO.LOW)
#             GPIO.output(ARM_STEP, GPIO.HIGH)
#             time.sleep(delay)
#             GPIO.output(ARM_STEP, GPIO.LOW)
#             time.sleep(delay)
#             total_steps += 1


def dispense(request):
    post_data = request.session.__getitem__("post_data")
    prescription_id = post_data.get("prescription_id")
    medicine_data = request.session.__getitem__('medicines')
    chamber_data = request.session.__getitem__("chamber_data")
    medicine_data_1 = request.session.__getitem__("dispense_details")
    dispensable_data = []
    for datas in medicine_data_1:
        qty = post_data.get(datas.get("medicine"))
        if qty:
            qty = int(qty)
            if qty > int(datas.get("max_dispensable_qty")):
                messages.error(request, datas.get("medicine") + " quantity should be less than " + str(datas.get(
                    "max_dispensable_qty")))
                return redirect("prescription_view", prescription_id)
    total = 0
    for datas in medicine_data_1:
        qty = post_data.get(datas.get("medicine"))
        if qty:
            qty = int(qty)
            price = float(datas.get("medicine_amount"))
            total += price * qty
    vacuum_1_count = None
    vacuum_2_count = None
    vacuum_3_count = None
    vacuum_4_count = None
    vacuum_5_count = None
    roller_right_count = None
    roller_left_count = None
    spring_1_count = None
    spring_2_count = None
    for data in medicine_data:
        qty = post_data.get(data)
        if qty:
            qty = int(qty)
            composition_id = int(post_data.get(data + "_composition"))
            multiplier = int(post_data.get(data + "_multiplier"))

            chambers = []
            for chamber in chamber_data:
                if chamber['medicine'] == data:
                    chambers.append(chamber)
            balance = qty
            for chamber in chambers:
                if balance == 0:
                    break
                rate = chamber['rate']
                if not rate:
                    continue
                if rate > balance:
                    continue
                quantity = chamber['available_qty']
                if balance < quantity:
                    rotations = balance / rate
                    balance = balance % rate
                else:
                    balance = qty % quantity
                    rotations = quantity / rate

                dict = {
                    "chamber_id": chamber['chamber_id'],
                    "prescription_id": prescription_id,
                    "medicine": chamber['medicine_id'],
                    "quantity": rotations * rate,
                    "load_data": chamber['load_data']
                }
                if multiplier != 1:
                    dict['actual_composition_id'] = composition_id
                dispensable_data.append(dict)
                if 'roller' in chamber['chamber']:
                    code = chamber['chamber'].replace("roller", "").strip()
                    code = code[1:].strip()
                    if code == 'right':
                        roller_right_count = rotations
                    elif code == 'left':
                        roller_left_count = rotations
                elif 'spring' in chamber['chamber']:
                    code = int(chamber['chamber'].replace('spring', ""))
                    if code == 1:
                        spring_1_count = rotations
                    elif code == 2:
                        spring_2_count = rotations
            vacuum_count = None
            for chamber in chambers:
                if balance == 0:
                    break
                if 'Vacuum Chamber' in chamber['chamber'] and not vacuum_count:
                    if balance <= 5:
                        if int(chamber['available_qty']) > balance:
                            vacuum_count = balance
                            code = int(chamber['chamber'].replace("Vacuum Chamber", "").strip())
                            if code == 1:
                                vacuum_1_count = balance
                            elif code == 2:
                                vacuum_2_count = balance
                            elif code == 3:
                                vacuum_3_count = balance
                            elif code == 4:
                                vacuum_4_count = balance
                            elif code == 5:
                                vacuum_5_count = balance

                            dict = {
                                "chamber_id": chamber['chamber_id'],
                                "prescription_id": prescription_id,
                                "medicine": chamber['medicine_id'],
                                "quantity": balance,
                                "load_data": chamber['load_data']
                            }
                            if multiplier != 1:
                                dict['actual_composition_id'] = composition_id
                            dispensable_data.append(dict)
                            balance = 0
                            break
                        else:
                            chamb_qty = int(chamber['available_qty'])
                            balance -= chamb_qty
                            code = int(chamber['chamber'].replace("Vacuum Chamber", "").strip())
                            if code == 1:
                                vacuum_1_count = chamb_qty
                            elif code == 2:
                                vacuum_2_count = chamb_qty
                            elif code == 3:
                                vacuum_3_count = chamb_qty
                            elif code == 4:
                                vacuum_4_count = chamb_qty
                            elif code == 5:
                                vacuum_5_count = balance

                            dict = {
                                "chamber_id": chamber['chamber_id'],
                                "prescription_id": prescription_id,
                                "medicine": chamber['medicine_id'],
                                "quantity": chamb_qty,
                                "load_data": chamber['load_data']
                            }
                            if multiplier != 1:
                                dict['actual_composition_id'] = composition_id
                            dispensable_data.append(dict)
    # if spring_1_count:
    #     #     # thread.start_new_thread(spring_1_dispense, (spring_1_count,))
    #     #     spring_1_dispense(spring_1_count)
    #     #     GPIO.cleanup()
    #     # if spring_2_count:
    #     #     # thread.start_new_thread(spring_2_dispense, (spring_2_count,))
    #     #     spring_2_dispense(spring_2_count)
    #     #     GPIO.cleanup()
    #     # if roller_right_count:
    #     #     # Backward is for right roller
    #     #     # thread.start_new_thread(roller_right_dispense, (roller_right_count,))
    #     #     roller_right_dispense(roller_right_count)
    #     #     GPIO.cleanup()
    #     # if roller_left_count:
    #     #     # Forward is for left roller
    #     #     # thread.start_new_thread(roller_left_dispense, (roller_left_count,))
    #     #     roller_left_dispense(roller_left_count)
    #     #     GPIO.cleanup()
    #     # if vacuum_1_count:
    #     #     temp = vacuum_1_count
    #     #     while temp > 0:
    #     #         vacuum(1)
    #     #         time.sleep(5)
    #     #         temp -= 1
    #     #         GPIO.cleanup()
    #     # if vacuum_2_count:
    #     #     temp = vacuum_2_count
    #     #     while temp > 0:
    #     #         vacuum(2)
    #     #         time.sleep(5)
    #     #         temp -= 1
    #     #         GPIO.cleanup()
    #     # if vacuum_3_count:
    #     #     temp = vacuum_3_count
    #     #     while temp > 0:
    #     #         vacuum(3)
    #     #         time.sleep(5)
    #     #         temp -= 1
    #     #         GPIO.cleanup()
    #     # if vacuum_4_count:
    #     #     temp = vacuum_4_count
    #     #     while temp > 0:
    #     #         vacuum(4)
    #     #         time.sleep(5)
    #     #         temp -= 1
    #     #         GPIO.cleanup()
    #     # if vacuum_5_count:
    #     #     temp = vacuum_5_count
    #     #     while temp > 0:
    #     #         vacuum(5)
    #     #         time.sleep(5)
    #     #         temp -= 1
    #     #         GPIO.cleanup()
    response = requests.post(SERVER_URL + "/api/v1/dispense_log", json=dispensable_data)
    if response.status_code == 200:
        messages.success(request, "Transaction Successful")
        return redirect('prescription_print_confirm', prescription_id)
    else:
        messages.error(request, "Error in Transaction " + response.json()['Error'])
        return redirect('prescription_list')
    # return redirect('prescription_view', prescription_id)


def bluetooth_control(request):
    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    advertise_service(server_sock, "iMedServer",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE],
                      #                   protocols = [ OBEX_UUID ]
                      )

    client_sock, client_info = server_sock.accept()
    try:
        while True:
            data = client_sock.recv(1024)
            global chamber
            try:
                data = int(data)
                if data == 4 and chamber == 0:
                    # Rotate Chamber 1
                    print("Chamber rotated " + str(CHAMBER_1_STEPS) + " steps")
                    # forward_chamber_vacuum(CHAMBER_1_STEPS)
                    chamber = 4
                elif data == 5 and chamber == 0:
                    # Rotate Chamber 2
                    print("Chamber rotated " + str(CHAMBER_2_STEPS) + " steps")
                    # forward_chamber_vacuum(CHAMBER_2_STEPS)
                    chamber = 5
                elif data == 6 and chamber == 0:
                    # Rotate Chamber 3
                    print("Chamber rotated backward" + str(CHAMBER_2_STEPS) + " steps")
                    # backward_chamber_vacuum(CHAMBER_2_STEPS)
                    chamber = 6
                elif data == 7 and chamber != 0:
                    # Reverse the corresponding Chamber
                    if chamber == 6:
                        print("Chamber rotated " + str(CHAMBER_2_STEPS) + " steps")
                        # forward_chamber_vacuum(CHAMBER_2_STEPS)
                    elif chamber == 5:
                        print("Chamber rotated backwards" + str(CHAMBER_2_STEPS) + " steps")
                        # backward_chamber_vacuum(CHAMBER_2_STEPS)
                    elif chamber == 4:
                        print("Chamber rotated backward" + str(CHAMBER_1_STEPS) + " steps")
                        # backward_chamber_vacuum(CHAMBER_1_STEPS)
                    chamber = 0
                client_sock.send("Success")
            except Exception, e:
                if data == 'end':
                    break
                client_sock.send("Error " + e.message)
    except IOError:
        pass

    client_sock.close()
    server_sock.close()
    return redirect('end_session')


def vendor_load(request):
    vendor_id = request.session.__getitem__("vendor_id")
    if not vendor_id:
        return redirect('landing_page')
    return render(request, 'admin_theme/vendor_load.html')


def end_session(request):
    for key in request.session.keys():
        del request.session[key]
    return redirect('landing_page')


def otc_pos(request):
    if request.method == 'POST':
        mobile_number = request.POST.get("mobile_number")
        request.session.__setitem__("mobile_number", mobile_number)
        return redirect('otc_payment')
    return render(request, 'admin_theme/mobile_number_enter.html')


def prescription_print_confirm(request, prescription_id):
    return render(request, 'admin_theme/prescription_confirm.html', {'prescription_id': prescription_id})


def prescription_print(request, prescription_id):
    # print_prescription(prescription_id)
    return redirect("end_session")


def temp_dispense_waiter(request):
    return render(request, "admin_theme/dispense_waiter.html")
