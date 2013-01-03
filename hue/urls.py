
from django.conf.urls.defaults import *
from webservices.hue.views import turn_on, turn_off, start_randomize, stop_randomize 

urlpatterns = patterns('',
    url(r'^$', turn_on),
    url(r'^turn_on$', turn_on),
    url(r'turn_off$', turn_off),
    url(r'randomize$', start_randomize),
    url(r'randomize/stop', stop_randomize), )
