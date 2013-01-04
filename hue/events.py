


def randomize_all_lights(hue, group_id, attrs):
    for light in hue.groups[group_id].lights:
        data = {}
        if not light.get_state_status('on'):
            light.turn_on()
        for attr in attrs:
            data[attr] = hue.get_light_attr_random(attr)
        hue.set_light_attr(light.id, data)
