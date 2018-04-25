# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import cv2
import keyboard
import pyzbar.pyzbar as pyzbar
import requests
from bluetooth import *
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime

from hardware import *

# Create your views here.

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
        cv2.namedWindow("QR", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("QR", cv2.WND_PROP_FULLSCREEN, 1)
        cv2.imshow("QR", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        data = decode(img)
        if data:
            keyboard.send("alt+tab")
            cv2.destroyAllWindows()
            cap.release()
            cv2.waitKey(1)

            return data


def CameraAccess(request):
    data = QRScanner()
    if "vendor" in data:
        request.session.__setitem__("vendor_id", data.split("-")[1])
        return redirect('vendor_load')
    else:
        request.session.__setitem__('aadhar_number', data)
        return redirect('verify_details')


def display_camera(request):
    return render(request, 'admin_theme/scan_camera.html')


def landing_page(request):
    return render(request, 'admin_theme/landing_page.html')


def dashboard(request):
    return render(request, 'admin_theme/dashboard.html')


def verify_details(request):
    aadhar = request.session.__getitem__('aadhar_number')
    if not aadhar:
        return redirect('landing_page')
    response = requests.get("http://10.1.75.239:8001/api/v1/user_details?aadhar_number=" + aadhar)
    data = None
    if response.status_code == 200:
        data = response.json()
    return render(request, 'admin_theme/verify_details.html', {'data': data, 'aadhar': aadhar})


def prescription_list(request):
    aadhar = request.session.__getitem__('aadhar_number')
    if not aadhar:
        return redirect('landing_page')
    response = requests.get("http://10.1.75.239:8001/api/v1/user_prescription?aadhar_number=" + aadhar)
    data = None
    if response.status_code == 200:
        request.session.__setitem__("prescription_data", response.json())
        received_data = response.json()
        data = []
        for prescription in received_data:
            doctor = prescription.get("doctor")
            created = prescription.get("created_at")
            doc_name = doctor.get("first_name") + " " + doctor.get("last_name")
            doc_pic = "http://10.1.75.239:8001" + doctor.get("profile_pic")
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
    response = requests.get("http://10.1.75.239:8001/api/v1/prescription?id=" + id + "&device_id=1")
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
    return render(request, 'admin_theme/composition_list.html',
                  {'datas': data, 'doctor': doctor, 'prescription_id': int(id)})


chamber = 0


def dispense(request, chamber_id, qty, prescription_id):
    # Chamber Movement
    global chamber
    data = chamber_id
    if data == 1:
        # Rotate Wheel

        pass
    elif data == 2:
        # Rotate Spring 1
        rotate_spring()
        pass
    elif data == 3:
        # Rotate Spring 2
        rotate_spring()
    else:
        rotate_chamber(data-3)
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
                    forward_chamber(DELAY, CHAMBER_1_STEPS)
                elif data == 5 and chamber == 0:
                    # Rotate Chamber 2
                    forward_chamber(DELAY, CHAMBER_2_STEPS)
                elif data == 6 and chamber == 0:
                    # Rotate Chamber 3
                    backwards_chamber(DELAY, CHAMBER_2_STEPS)
                elif data == 7 and chamber != 0:
                    # Reverse the corresponding Chamber
                    if chamber == 6:
                        forward_chamber(DELAY, CHAMBER_2_STEPS)
                    elif chamber == 5:
                        backwards_chamber(DELAY, CHAMBER_2_STEPS)
                    elif chamber == 4:
                        backwards_chamber(DELAY, CHAMBER_1_STEPS)
                    chamber = 0
                if data == 'end':
                    break
                client_sock.send("Success")
            except Exception, e:
                client_sock.send("Error")
    except IOError:
        pass

    client_sock.close()
    server_sock.close()
    for key in request.session.keys():
        del request.session[key]
    return redirect('landing_page')


def vendor_load(request):
    vendor_id = request.session.__getitem__("vendor_id")
    if not vendor_id:
        return redirect('landing_page')
    return render(request, 'admin_theme/vendor_load.html')
