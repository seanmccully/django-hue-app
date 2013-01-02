"""
Hue Exceptions
"""



class InvalidLightAttr(Exception):
    def __init__(self, message):
        self.message = "Invalid Hue Light Attribute [%s]" % message


class InvalidLightAttrValue(Exception):
    def __init__(self, key, value):
        self.message = "Hue Light Attribute out of allowed range [%s] [%s]" % (key, value)


class InvalidHueHub(Exception):
    pass

class InvalidHueSchedule(Exception):
    pass

class HueLightDoesNotExist(Exception):
    pass

class HueGroupDoesNotExist(Exception):
    pass

class HueScheduleDoesNotExist(Exception):
    pass

class HueError(Exception):
    pass

class HueGroupReadOnly(Exception):
    pass
