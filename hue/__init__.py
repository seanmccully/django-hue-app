"""
(c) 2013 Sean McCully
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Also licenced under the Apache License, 2.0: http://opensource.org/licenses/apache2.0.php
# Licensed to PSF under a Contributor Agreement
Base Hue

"""

from urllib.request import Request
from urllib import request
from random import randint, uniform
from webservices.hue.exceptions import (InvalidLightAttr, InvalidLightAttrValue,
                                InvalidHueHub, HueLightDoesNotExist,
                                HueGroupDoesNotExist, HueError,
                                HueGroupReadOnly, InvalidHueSchedule)
from urllib.error import HTTPError, URLError
from socket import timeout
from datetime import datetime, timedelta
import json


FRMT_STR = '%Y-%m-%dT%I:%M:%S'
ALLOWED_STATES = { 'on' : bool,
                   'bri' : [0, 254],
                    'hue' : [0, 65535],
                    'sat' : [0, 254],
                    'xy' : [0, 0.9],
                    'ct' : [154, 500],
                    'alert' : ('select', 'lselect'),
                    'effect' : (None, ),
                    'reachable' : bool }

class HueLight:
    """A Hue Light"""

    def __init__(self, id, url, light_data=None):
        """Initialize Object to represent a Hue Light"""
        self.id = id
        self.uri = '/lights/%d' % self.id
        self.state_url = url + self.uri + '/state'
        if light_data:
            self.name = light_data['name']
            self.model_id = light_data['modelid']
            self.version = light_data['swversion']
            self.light_type = light_data['type']
            self.point_symbols = light_data['pointsymbol']
            self.state = light_data['state']


    def get_point(self, pointno=None):
        try:
            if not pointno:
                return self.point_symbols
            elif pointno in self.point_symbols:
                return self.point_symbols[pointno]
            else:
                return None
        except AttributeError:
            return None
 

    def get_state_status(self, state_attr=None):
        """Get current light value for state attr"""
        try:
            if not state_attr:
                return self.state
            elif state_attr in self.state:
                return self.state[state_attr]
            else:
                return None
        except AttributeError:
            return None

    def turn_on(self):
        """Turn Light On"""
        req = Request(self.state_url, 
                    data=bytearray('{ "on" : true}', 'utf-8'))
        req.get_method = lambda: 'PUT'
        response = request.urlopen(req)
        return response.read()

    def turn_off(self):
        """Turn Light Off"""
        req = Request(self.state_url, 
                    data=bytearray('{ "on" : false}', 'utf-8'))
        req.get_method = lambda: 'PUT'
        response = request.urlopen(req)
        return response.read()


class HueConfig:
    """Current Hue Config"""

    def __init__(self, config_data):
        """Load Hue Config"""
        self.dhcp = config_data['dhcp']
        self.gateway = config_data['gateway']
        self.ip_addr = config_data['ipaddress']
        self.link_button = config_data['linkbutton']
        self.mac = config_data['mac']
        self.name = config_data['name']
        self.netmask = config_data['netmask']
        self.portalservice = config_data['portalservices']
        self.proxy_addr = config_data['proxyaddress']
        self.swupdate = config_data['swupdate']
        self.version = config_data['swversion']
        self.whitelist = config_data['whitelist']


class HueGroup:
    """Represent a Hue Grouping of Lights"""

    def __init__(self, key, name, lights, read_only=False):
        """Represents a Grouping of Hue Lights"""
        self.id = key
        self.name = name
        self.lights = lights
        self.uri = "/groups/%s" % self.id
        self.read_only = read_only


class HueCommand:
    """ A command for use in schedules"""

    def __init__(self, address, body, method='PUT'):
        """Represent a Hue Command
            -address [uri where command is to be executed at]
            -body [data to be sent with command]
            -method [How HTTP request should be sent default PUT]
        """
        self.address = address
        self.body = body
        self.method = method

    def __dict__(self):
       return { 'address' : self.address,
                'body' : self.body,
                'method' : self.method }

class HueSchedule:
    """ Represent a Schedule for Hue Hub """

    def __init__(self, key, name, description,
                        time_stamp, command, read_only=False):
        """A Hue Schedule object"""
        self.id = key
        self.name = name
        self.uri = "/schedules/%s" % self.id
        self.description = description
        self.date_time = datetime.strptime(time_stamp, FRMT_STR)
        if type(command) == dict:
            try:
                self.command = HueCommand(command['address'],
                                            command['body'],
                                            command['method'])
            except KeyError as key_err:
                raise InvalidHueSchedule
        elif type(command) == HueCommand:
            self.command = command
        else:
            raise InvalidHueSchedule

    def get_iso_time(self):
        return self.date_time.isoformat()


class Hue:
    """Object Representing Hue Interface"""

    def __init__(self, host, app_key, port=80, load_now=True):
        """Initialize Object for communicating with Hue Base Station"""
        self.app_key = app_key
        self.host = host
        self.port = port
        self.uri = '/api/%s' % self.app_key
        self.url = 'http://%s:%d%s' % (self.host, self.port, self.uri)
        self.lights = {}
        self.groups = {}
        self.schedules = {}
        self.config = None
        if load_now:
            self.load_hue()

    def _connect_hue(self, url, data=None, method=None):
        """Connect To Hue Hub"""
        try:
            req = Request(url)
        except ValueError as exc:
            raise HueError(exc)
        if data:
            json_str = json.dumps(data)
            json_bytes = bytearray(json_str, 'utf-8')
            req.add_data(json_bytes)
        if method:
            req.get_method = lambda : method
        try:
            response = request.urlopen(req)
            return response.read()
        except (HTTPError, URLError) as error:
            raise InvalidHueHub(error)
        except timeout as error:
            raise InvalidHueHub(error)
        except NameError as error:
            raise HueError(error)

    def load_hue(self):
        """Load default Hue Response into Hue objects"""
        resp = self._connect_hue(self.url)
        resp = self._load_json(resp.decode('utf-8'))
        self._load_lights(resp['lights'])
        self._load_config(resp['config'])
        self._load_groups(resp['groups'])
        self._load_schedules(resp['schedules'])

    def _load_json(self, str_data):
        """Load json string into python data"""
        doc = json.loads(str_data)
        return doc

    def _load_lights(self, lights_dict):
        """Load Hue Lights into HueLight Objects"""
        for key in lights_dict.keys():
            self.lights[key] = HueLight(int(key), self.url, lights_dict[key])

    def _load_config(self, config):
        """Load Hue Config data into HueConfig object"""
        self.config = HueConfig(config)

    def _load_groups(self, groups):
        """Load Hue Groups into HueGroup objects"""
        def load_lights(light_ids):
            lights = []
            try:
                for light_id in light_ids:
                    lights.append(self.lights[light_id])
            except KeyError as key_err:
                raise HueLightDoesNotExist(key_err)

        for key in groups.keys():
            lights = load_lights(groups[key]['lights'])
            self.groups[key] = HueGroup(key, groups[key]['name'], lights)
        if '0' not in groups:
            #There exists a 0 zero group of all lights
            group_zero = \
            self._connect_hue(self.url + '/groups/0').decode('utf-8')
            group_zero = json.loads(group_zero)
            lights = load_lights(group_zero['lights'])
            self.groups['0'] = HueGroup('0', group_zero['name'],
                                                lights, read_only=True)


    def _load_schedules(self, schedules):
        """Load Hue Schedule into HueSchedule Objects"""
        for schedule in schedules.keys():
            try:
                hue_schedule = HueSchedule(schedule, schedules[schedule]['name'],
                                    schedules[schedule]['description'], 
                                    schedules[schedule]['time'],
                                    schedules[schedule]['command'])
                self.schedules[schedule] = hue_schedule
            except KeyError as key_err:
                raise HueError(key_err)

    def set_light_attr(self, light_id, attr):
        """Set a current HueLight Object to accepted Hue attrs"""
        if light_id in self.lights:
            light_url = '%s%s/state' % (self.url, self.lights[light_id].uri)
            for key in attr.keys():
                try:
                    if type(ALLOWED_STATES[key]) == bool:
                        if attr[key] not in (True, False):
                            raise InvalidLightAttrValue(key, attr[key])
                    elif type(ALLOWED_STATES[key]) == tuple:
                        if attr[key] not in ALLOWED_STATES[key]:
                            raise InvalidLightAttrValue(key, attr[key])
                    else:
                        if not self._compare(attr[key], ALLOWED_STATES[key]):
                            raise InvalidLightAttrValue(key, attr[key])
                except KeyError as key_err:
                    raise InvalidLightAttr(key_err.args)
            response = self._connect_hue(light_url, data=attr, method='PUT')
            return response
        else:
            return None

    def get_light_attr_random(self, attr):
        """Take a Hue Light attr and get a random value in accepted range"""
        try:
            if type(ALLOWED_STATES[attr]) == list:
                allowed_range = ALLOWED_STATES[attr]
                if type(allowed_range[1]) == int:
                    rand_func = randint
                else:
                    rand_func = uniform
                return rand_func(allowed_range[0], allowed_range[1])
            elif type(ALLOWED_STATES[attr]) == bool:
                return randint(0, 1) == True
            elif type(ALLOWED_STATES[attr]) == tuple:
                range_x = len(ALLOWED_STATES[attr]) -1
                return ALLOWED_STATES[attr][randint(0, range_x)]
        except KeyError as key_err:
            raise InvalidLightAttr(key_err.args)

    def delete_group(self, group_key):
        """Delete a Hue lighting group"""
        try:
            if not self.groups[group_key].read_only:
                group_uri = self.groups[group_key].uri
                url = "%s%s" % (self.url, group_uri)
                resp = self._connect_hue(url, method='DELETE').decode('utf-8')
                resp = json.loads(resp)
                if 'success' in resp:
                    del self.groups[group_key]
            else:
                raise HueGroupReadOnly
        except KeyError as key_err:
            raise HueGroupDoesNotExist(key_err)

    def delete_schedule(self, schedule_key):
        """Delete a scheduled Hue event"""
        try:
            schedule = self.schedules[schedule_key]
            url = "%s%s" % (self.url, schedule.uri)
            resp = self._connect_hue(url, method='DELETE').decode('utf-8')
            resp = json.loads(resp)[0]
            if 'success' in resp:
                del self.schedules[schedule_key]
        except KeyError:
            raise HueScheduleDoesNotExist

    def create_group(self, lights, group_name):
        """Create a new Hue group of lights
            -lights [list of HueLights]
            -group_name [Name of hue group]"""
        try:
            url = "%s/groups" % self.url
            light_keys = []
            for light in lights:
                light_keys.append(str(light.id))
            data = { "lights" : light_keys, "name" : group_name }
            resp = self._connect_hue(url, data=data)
            resp = resp.decode('utf-8')
            data_resp = json.loads(resp)
            if 'success' in data_resp[0]:
                group_id = data_resp[0]['success']['id']
                group_id = group_id.split('/')[-1]
                self.groups[group_id] = HueGroup(group_id, group_name, lights)
        except IndexError:
            raise HueError

    def create_schedule(self, name, commands, description=None,
                        time=None, repeats=None):
        """
            Register HueSchedules with HueCommands
            -name [Name of the Schedule]
            -commands [List of HueCommands]
            -description [Description optional N/A used if not provided]
            -time [datetime object]
            -repeats [optional dict with keys times = times to repeats,
                        interval dict of interval parameters]
        """
        if repeats:
            try:
                if repeats['times'] > 1:
                    repeats['times'] -= 1
                    self.create_schedule(name, commands, description=description,
                        time=time + timedelta(**repeats['interval']),
                        repeats=repeats)
                else:
                    self.create_schedule(name, commands, description=description,
                        time=time + timedelta(**repeats['interval']),
                        repeats=None)
            except KeyError:
                raise InvalidHueSchedule
        if time == None:
           time_str = (datetime.now() + timedelta(days=1)).strftime(FRMT_STR)
        else:
            try:
                time_str = time.strftime(FRMT_STR)
            except AttributeError:
                raise InvalidHueSchedule
        if not description:
            description = 'N/A'
        url = self.url + '/schedules'
        for command in commands:
            data = { 'command' : command.__dict__(),
                        'description' : description,
                        'name' : name, 
                        'time' : time_str}
            resp = self._connect_hue(url, data=data).decode('utf-8')
            resp = json.loads(resp)[0]
            if 'success' in resp:
                schedule_id = resp['success']['id'].split('/')[-1]
                self.schedules[schedule_id] = HueSchedule(schedule_id, name,
                                                description, time_str, command)


    def edit_group_lights(self, lights, group_id):
        """Add/Remove Lights from a Hue Group
            -lights [list of lights in Hue Group]
            -group_id [Hue group id]"""
        url = "%S/groups/%s" % (self.url, group_ip)
        light_keys = []
        for light in lights:
            light_keys.append(str(light.id))
        data = { "lights" : light_keys }
        resp = self._connect_hue(url, data=light_keys, method='PUT')
        resp = resp.decode('utf-8')
        resp = json.loads(resp)
        if 'success' in resp:
            try:
                self.groups[group_id].lights = lights
            except KeyError as key_err:
                raise HueError(key_err)

    def _compare(self, val, accepted_values):
        """Compare Value to accepted Range"""
        if type(val) in (list, tuple):
            ret_val = True
            for value in val:
                ret_val = self._compare(value, accepted_values)
                if not ret_val:
                    return ret_val
            return ret_val
        elif type(val) == accepted_values:
            return True
        elif float(val) >= accepted_values[0] \
                    and float(val) <= accepted_values[1]:
            return True
        else:
            return False

