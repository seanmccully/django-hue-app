# Create your views here.


from django.conf import settings
from hue import Hue
from hue.events import randomize_all_lights
from django.http import HttpResponse, Http404
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

def start_randomize(request, group_id=0, secs=1):
    hue = Hue(settings.HUE_HOST, settings.HUE_APP_KEY, port=settings.HUE_PORT)
    looping_call = LoopingCall(randomize_all_lights,
                        *(hue, str(group_id), ['hue', 'sat'], ))
    looping_call.start(int(secs))
    settings.TWISTED_STACK.append(looping_call)
    return HttpResponse('Looping Call Started')

def stop_randomize(request, pos=-1):
    try:
        if pos==-1:
            looping_call = settings.TWISTED_STACK.pop()
        else:
            looping_call = settings.TWISTED_STACK[pos]
            del settings.TWISTED_STACK[pos]
        if looping_call.running:
            looping_call.stop()
        return HttpResponse(len(settings.TWISTED_STACK))
    except IndexError:
        raise Http404

def reactor_running(request):
    return HttpResponse(reactor.running)

