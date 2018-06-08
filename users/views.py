# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import cv2
import pyzbar.pyzbar as pyzbar
import requests
from bluetooth import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime

# Create your views here.
from iMedAtm import settings
from iMedAtm.settings import SERVER_URL

# from hardware import *

# from hardware import *

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
        return redirect('pin_enter')
    # time.sleep(10)
    # return redirect('verify_details')


def display_camera(request):
    return render(request, 'admin_theme/scan_camera.html')


def middle(request):
    return render(request, 'admin_theme/middle.html')


def landing_page(request):
    return render(request, 'admin_theme/landing_page.html')


def dashboard(request):
    return render(request, 'admin_theme/dashboard.html')


def pin_enter(request):
    aadhar = request.session.__getitem__('aadhar_number')
    if not aadhar:
        return redirect('landing_page')
    if request.method == 'POST':
        pin = request.POST.get("password")
        response = requests.post(SERVER_URL + "/api/v1/authenticate", {'aadhar': aadhar, 'pin': pin})
        if response.status_code == 200:
            request.session.__setitem__('user', response.json())
            return redirect('verify_details')
        else:
            messages.error(request, "Wrong Credentials")
    return render(request, 'admin_theme/pin_enter_page.html')


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
    if not prescription_data:
        return redirect('landing_page')
    doctor = None
    for data in prescription_data:
        data_id = int(data.get('id'))
        if data_id == int(id):
            doctor = data.get("doctor")
            break
    data = response.json()
    request.session.__setitem__("chamber_data", data.get("chamber_data"))
    request.session.__setitem__("dispense_details", data.get("prescription_data"))
    request.session.__setitem__("medicines", data.get("medicines"))
    data = data.get("prescription_data")
    return render(request, 'admin_theme/composition_list.html',
                  {'datas': data, 'doctor': doctor, 'prescription_id': int(id)})


chamber = 0
ROLLER_STEP_COUNT = 50


def dispense(request):
    if request.method == 'POST':
        prescription_id = request.POST.get("prescription_id")
        medicine_data = request.session.__getitem__('medicines')
        chamber_data = request.session.__getitem__("chamber_data")
        dispensable_data = []
        for data in medicine_data:
            qty = request.POST.get(data)
            if qty:
                chambers = []
                for chamber in chamber_data:
                    if chamber['medicine'] == data:
                        chambers.append(chamber)
                vacuum_1_count = None
                vacuum_2_count = None
                vacuum_3_count = None
                vacuum_4_count = None
                roller_right_count = None
                roller_left_count = None
                spring_1_count = None
                spring_2_count = None
                balance = qty
                for chamber in chambers:
                    rate = chamber['rate']
                    quantity = chamber['quantity']
                    if balance < quantity:
                        balance = qty % quantity
                        temp = qty - balance
                        rotations = temp / rate
                    else:
                        rotations = quantity / rate
                        balance -= quantity
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
                    if 'Vacuum Chamber' in chamber['chamber'] and not vacuum_count:
                        if balance < 5:
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
        return redirect('prescription_view', prescription_id)


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


def session(request):
    return render(request, 'admin_theme/shell.php')
