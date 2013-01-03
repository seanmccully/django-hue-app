# Create your views here.


from django.conf import settings
from hue import Hue
from hue.events import randomize_all_lights
from django.http import HttpResponse
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

def turn_on(request, light=None):
    hue = Hue(settings.HUE_HOST, settings.HUE_APP_KEY, port=settings.HUE_PORT)
    if not light:
        for light_id in hue.lights:
            hue.lights[light_id].turn_on()
    else:
        hue.lights[light].turn_on()

    return HttpResponse('Success')


def turn_off(request, light=None):
    hue = Hue(settings.HUE_HOST, settings.HUE_APP_KEY, port=settings.HUE_PORT)
    if not light:
        for light_id in hue.lights:
            hue.lights[light_id].turn_off()
    else:
        hue.lights[light].turn_off()

    return HttpResponse('Success')



def start_randomize(request, secs=1):
    hue = Hue(settings.HUE_HOST, settings.HUE_APP_KEY, port=settings.HUE_PORT)
    looping_call = LoopingCall(randomize_all_lights, *(hue, ['hue', 'sat'], ))
    looping_call.start(secs)
    settings.TWISTED_STACK.append(looping_call)
    return HttpResponse('Looping Call Started')


def stop_randomize(request):
    looping_call = settings.TWISTED_STACK.pop()
    looping_call.stop()
    return HttpResponse('Looping Call Stopped')


def reactor_running(request):
    return HttpResponse(reactor.running)
