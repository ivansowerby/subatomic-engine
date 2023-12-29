from typing import Union
from os import urandom
from base58 import b58encode
from collections import defaultdict 
from json import dumps, loads
from pickle import dump, load, HIGHEST_PROTOCOL
from math import inf

class Viewport:
    LOWEST_PRIORITY_LEVEL = 0
    HIGHEST_PRIORITY_LEVEL = inf

    def __init__(self, width: int, height: int) -> None:
        self.x, self.y, self.z = 0, 0, 0
        self.width, self.height = width, height
    
    def position(self, x: int, y: int, z: int) -> None:
        self.x, self.y, self.z = x, y, z
    
    def resize(self, width: int, height: int) -> None:
        self.width, self.height = width, height

class Ludus(Viewport):
    UID = 'u'
    GID = 'g'

    def __init__(self, encoded: bool = True) -> None:
        self.encoded = encoded
        self.objects = defaultdict(lambda: defaultdict(list))
        self.__grouping__()
        self.attributes = defaultdict(lambda: defaultdict(dict))
    
    def __dictionary__(self, obj: Union[dict, object]) -> dict:
        if type(obj) == dict: return obj
        elif isinstance(obj, object):
            if not self.encoded: return {object: obj}
            else: return vars(obj)
        else: return {}
        
    def is_id(id: str, prefix: str) -> bool:
        if '-' not in id: return False
        return prefix == id[:id.rfind('-')]
    
    def __id__(prefix: str, n: int = 16) -> str:
        id = b58encode(urandom(n)).decode('UTF-8')
        return f'{prefix}-{id}'
    
    def new_object(self) -> str:
        return Ludus.__id__(Ludus.UID)

    def new_group(self, priority_level: Union[int, float] =  Viewport.HIGHEST_PRIORITY_LEVEL) -> str:
        gid = Ludus.__id__(Ludus.GID)
        self.add_attribute(gid, {'priority-level': priority_level})
        return gid

    def get(self, id: str) -> dict:
        object = {}
        if Ludus.is_id(id, Ludus.UID): object = self.objects[id]
        elif Ludus.is_id(id, Ludus.GID): object = self.groups[id]
        return object
    
    def add_object(self, properties: Union[dict, object] = {}, gid: list = None) -> str:
        properties = self.__dictionary__(properties)
        uid = self.new_object()
        values = defaultdict(None)
        values.update({'gid': [], **properties})
        self.objects.update({uid: values})
        if gid != None: self.attach_group(uid, gid)
        return uid

    def remove_object(self, uid: str) -> None:
        gid = self.objects[uid]['gid']
        for group in gid:
            self.groups[group].remove(uid)
            if len(self.groups[group]) == 0: del self.groups[group]
        del self.objects[uid]
        
    def add_property(self, uid: str, properties: Union[dict, object]) -> None:
        properties = self.__dictionary__(properties)
        self.objects[uid].update(properties)

    def remove_property(self, uid: str, properties: list) -> None:
        [self.objects[uid].pop(property, None) for property in properties]

    def clear_properties(self, uid: str) -> None:
        self.objects[uid].clear()

    def attach_group(self, uid: str, gid: Union[str, list], attributes: dict = {}, priority_level: Union[int, float] = Viewport.HIGHEST_PRIORITY_LEVEL) -> None:
        if type(gid) == str: gid = [gid]
        self.objects[uid]['gid'].extend(gid)
        for group in gid:
            self.groups[group].append(uid)
            self.attributes[group].update(attributes)
            if self.attributes[group]['priority-level'] != {}: continue
            self.attributes[group]['priority-level'] = priority_level
    
    def detach_group(self, uid: str, gid: list) -> None:
        if type(gid) == str: gid = [gid]
        groups = self.objects[uid]['gid']
        groups = [group for group in groups if group not in gid]
        self.objects[uid]['gid'] = groups
        for group in gid:
            self.groups[group].remove(uid)
            if len(self.groups[group]) == 0:
                del self.groups[group]
                del self.attributes[group]
    
    def add_attribute(self, gid: str, attributes: Union[dict, object]) -> None:
        attributes = self.__dictionary__(attributes)
        self.attributes[gid].update(attributes)
    
    def remove_attribute(self, gid: str, attributes: list) -> None:
        [self.attributes[gid].pop(attribute, None) for attribute in attributes]

    def clear_attributes(self, gid: str) -> None:
        self.attributes[gid].clear()
    
    def by(self, key: str) -> dict:
        objects = defaultdict(list)
        items = sorted(self.objects.items(), key = lambda pair: max([self.attributes[group]['priority-level'] for group in pair[1]['gid']]))
        for uid, values in items:
            for value in values[key]: objects[tuple(value)] = uid
        return objects

    def __grouping__(self) -> None:
        self.groups = defaultdict(list)
        for uid, values in self.objects.items():
            groups = values['gid']
            for gid in groups:
                self.groups[gid].append(uid)

    def serialize(self, indent: int = 0) -> str:
        return dumps(self.objects, indent = indent)
    
    def deserialize(self, objects: str) -> None:
        self.objects = loads(objects)
        self.__grouping__()
    
    def dump(self, handle) -> None:
        dump(self.objects, handle, protocol = HIGHEST_PROTOCOL)
        handle.close()
    
    def load(self, handle) -> None:
        self.objects = load(handle)
        self.__grouping__()