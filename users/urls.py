from django.conf.urls import url
from .views import *
urlpatterns = [

    url(r'^display_camera$', display_camera, name='display_camera'),
    url(r'^dashboard$', dashboard),
    url(r'^prescription_list/(?P<user_id>[0-9]+)',prescription_list,name='prescription_list'),

]
