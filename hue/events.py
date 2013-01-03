


def randomize_all_lights(hue, attrs):
    for light in hue.lights:
        data = {}
        for attr in attrs:
            data[attr] = hue.get_light_attr_random(attr)
        hue.set_light_attr(light, data)
