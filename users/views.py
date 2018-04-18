# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from subprocess import call

import requests
from django.http import HttpResponse
from django.shortcuts import render


def display_camera(request):
    call(['python', '/home/pi/iMedDispenser/imedDispenserHardware'])
    return HttpResponse("Display Camera")


def landing_page(request):
    return render(request, 'admin_theme/landing_page.html')


def dashboard(request):
    return render(request, 'admin_theme/dashboard.html')


def prescription_list(request, user_id):
    response = requests.get("http://10.1.75.239:8000/api/v1/prescription_list", params={'user_id': user_id})
    if response.status_code == 200:
        data = response.json()
