


def randomize_all_lights(group, attrs):
    for light in group.lights:
        data = {}
        if not light.get_state_status('on'):
            light.turn_on()
        for attr in attrs:
            data[attr] = light.get_light_attr_random(attr)
        light.set_light_attr(data)
