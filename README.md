django-hue-app
==============
Python Django App for communicating with Philips Hue base station.
======================================================================
Initialize a Hue object with the ip address of your Hue base station 
your hue app key, and port if needed. Hue will load all configuration,
lights, groups, and schedules by default. Hue groups and schedules can be created
with minimal configuration. A hue group is created with a list of lights, a Hue
Schedule is created with a list of HueCommands and a datetime object.


`hue = Hue('192.168.1.102','some-hue-key', port=80)`

`hue.lights['0'].set_light_attr('1', { 'hue' : 6233, 'bri' : 200 })`

`hue.lights['1'].set_light_attr('1', { 'hue' : hue.['1'].get_light_attr_random('hue'), 'bri' : 200 })`

`lights = [hue.lights[light_key] for light_key in hue.lights.keys()]`

`hue.create_group(lights, 'Test Group')`

`hue.groups['1'].delete()`

`commands = [HueCommand(hue.lights[key].uri + '/state', { 'hue' : 0, 'sat' : 10}, 'PUT') for key in hue.lights.keys()]`

`hue.create_schedule('test', commands, time=datetime.now() + timedelta(seconds=20))`

`hue.scan_lights()`
