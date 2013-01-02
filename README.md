django-hue-app
==============
Python 3.X Django App for communicating with Philips Hue base station.
======================================================================

+hue = Hue('192.168.1.102','some-hue-key', port=80)
+hue.set_light_attr('1', { 'hue' : 6233, 'bri' : 200 })
+hue.set_light_attr('1', { 'hue' : hue.get_light_attr_random('hue'), 'bri' : 200 })
+hue.create_group(lights, 'Test Group')
+hue.delete_group(hue.groups.keys()[1])

