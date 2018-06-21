from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='pos_index'),
    url(r'^payment$', views.payment, name='otc_payment'),
    url(r'^dispense_waiter', views.temp_dispense_waiter, name='otc_dispense_waiter'),
    url(r'^otc_payment_wait/(?P<payment_request_id>[-\w]+)$', views.otc_payment_wait, name='otc_payment_wait'),
    url(r'^otc_dispense', views.otc_dispense, name='otc_dispense'),
]
