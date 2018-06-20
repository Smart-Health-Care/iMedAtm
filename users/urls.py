from django.conf.urls import url

from .views import *

urlpatterns = [

    url(r'^display_camera$', display_camera, name='display_camera'),
    # url(r'^dashboard$', dashboard),
    url(r'^prescription_list', prescription_list, name='prescription_list'),
    url(r'^launch_camera', CameraAccess, name='launch_camera'),
    url(r'^verify_details', verify_details, name='verify_details'),
    url(r'^prescription_view/(?P<id>[0-9]+)', prescription_view, name='prescription_view'),
    url(r'^payment/(?P<total>[0-9]+)$', payment, name='payment'),
    url(r'^payment_confirm$', payment_confirmation, name='payment_confirmation'),
    # url(r'^dispense/(?P<chamber_id>[0-9]+)/(?P<qty>[0-9]+)/(?P<prescription_id>[0-9]+)', dispense, name='dispense'),
    url(r'^dispense', dispense, name='dispense'),
    url(r'^vendor_load', vendor_load, name='vendor_load'),
    url(r'^bluetooth_control', bluetooth_control, name='bluetooth_control'),
    url(r'^end_session', end_session, name='end_session'),
    url(r'^verify_pin', pin_enter, name='pin_enter'),
    url(r'^payment_wait/(?P<payment_request_id>[-\w]+)', payment_wait, name='payment_wait'),
    url(r'^otc_pos', otc_pos, name='otc_pos')
]
