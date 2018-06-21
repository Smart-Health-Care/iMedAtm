import time
from datetime import datetime, timedelta

import pytz
import requests
# from RPi import GPIO
from django.contrib import messages
from django.shortcuts import render, redirect
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from iMedAtm import settings
from iMedAtm.settings import SERVER_URL
# from users.views import vacuum, roller_left_dispense, roller_right_dispense, spring_2_dispense, spring_1_dispense


def index(request):
    return render(request, 'pos/index.html', {'mobile_number': 9597267499})


class GetOTCMedicines(APIView):
    def get(self, request):
        response = requests.get(SERVER_URL + "/doctor/otc_medicine_list?device_id=" + str(settings.DEVICE_ID))
        if response.status_code == 200:
            return Response(response.json())


class FinishBill(APIView):
    def post(self, request):
        data = request.data.get("products")
        request.session.__setitem__("products", data)
        total = 0
        items = []
        for product in data:
            qty = int(product.get("qty"))
            price = product.get("price")
            stock = int(product.get("stock"))
            remaining = stock - qty
            total += (qty * price)
            items.append({'id': product.get("id"), "stock": remaining})
        request.session.__setitem__("total", total)
        datas = {"status": "success", "message": "Confirm Payment of Rs." + str(total), 'data': items}
        return Response(datas)


def payment(request):
    total = request.session.__getitem__("total")
    mobile_number = request.session.__getitem__("mobile_number")
    response = requests.post(SERVER_URL + "/users/api/v1/initialize_payment",
                             data={'amount': total, 'mobile_number': mobile_number})
    if response.status_code == 200:
        payment_request_id = response.json().get("id")
        return redirect('otc_payment_wait', payment_request_id)
    else:
        messages.error(request, "Error Processing Payment")
        return redirect('end_session')


def otc_payment_wait(request, payment_request_id):
    date = datetime.now() + timedelta(minutes=5)
    asia = pytz.timezone("Asia/Kolkata")
    date_string = pytz.utc.localize(date).astimezone(asia).strftime("%a %b %d %Y %H:%M:%S GMT %z")
    check_payment_url = SERVER_URL + "/users/api/v1/check_payment?payment_request_id=" + payment_request_id
    return render(request, 'pos/otc_payment_wait.html',
                  {'check_url': check_payment_url, "date_string": date_string})


def otc_dispense(request):
    dispensable_data = []
    vacuum_1_count = None
    vacuum_2_count = None
    vacuum_3_count = None
    vacuum_4_count = None
    vacuum_5_count = None
    roller_right_count = None
    roller_left_count = None
    spring_1_count = None
    spring_2_count = None
    response = requests.get(SERVER_URL + "/api/v1/device_chamber_data?device_id=" + str(settings.DEVICE_ID))
    chamber_data = response.json()
    products = request.session.__getitem__("products")
    for data in products:
        qty = data.get("qty")
        if qty:
            qty = int(qty)
            chambers = []
            for chamber in chamber_data:
                if chamber['medicine'] == data['medicine_name']:
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
                    "medicine": chamber['medicine_id'],
                    "quantity": rotations * rate,
                    "load_data": chamber['load_data']
                }
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
                                "medicine": chamber['medicine_id'],
                                "quantity": balance,
                                "load_data": chamber['load_data']
                            }
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
                                vacuum_5_count = chamb_qty
                            dict = {
                                "chamber_id": chamber['chamber_id'],
                                "medicine": chamber['medicine_id'],
                                "quantity": chamb_qty,
                                "load_data": chamber['load_data']
                            }
                            dispensable_data.append(dict)

    # if spring_1_count:
    #     # thread.start_new_thread(spring_1_dispense, (spring_1_count,))
    #     spring_1_dispense(spring_1_count)
    #     GPIO.cleanup()
    # if spring_2_count:
    #     # thread.start_new_thread(spring_2_dispense, (spring_2_count,))
    #     spring_2_dispense(spring_2_count)
    #     GPIO.cleanup()
    # if roller_right_count:
    #     # Backward is for right roller
    #     # thread.start_new_thread(roller_right_dispense, (roller_right_count,))
    #     roller_right_dispense(roller_right_count)
    #     GPIO.cleanup()
    # if roller_left_count:
    #     # Forward is for left roller
    #     # thread.start_new_thread(roller_left_dispense, (roller_left_count,))
    #     roller_left_dispense(roller_left_count)
    #     GPIO.cleanup()
    # if vacuum_1_count:
    #     temp = vacuum_1_count
    #     while temp > 0:
    #         vacuum(1)
    #         time.sleep(5)
    #         temp -= 1
    #         GPIO.cleanup()
    # if vacuum_2_count:
    #     temp = vacuum_2_count
    #     while temp > 0:
    #         vacuum(2)
    #         time.sleep(5)
    #         temp -= 1
    #         GPIO.cleanup()
    # if vacuum_3_count:
    #     temp = vacuum_3_count
    #     while temp > 0:
    #         vacuum(3)
    #         time.sleep(5)
    #         temp -= 1
    #         GPIO.cleanup()
    # if vacuum_4_count:
    #     temp = vacuum_4_count
    #     while temp > 0:
    #         vacuum(4)
    #         time.sleep(5)
    #         temp -= 1
    #         GPIO.cleanup()
    # if vacuum_5_count:
    #     temp = vacuum_5_count
    #     while temp > 0:
    #         vacuum(5)
    #         time.sleep(5)
    #         temp -= 1
    #         GPIO.cleanup()
    response = requests.post(SERVER_URL + "/api/v1/dispense_log", json=dispensable_data)
    messages.success(request, 'Transaction Complete')
    return redirect('end_session')


def temp_dispense_waiter(request):
    return render(request, "pos/dispense_waiter.html")
