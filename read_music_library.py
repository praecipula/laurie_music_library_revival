#!/usr/bin/env python3
from lxml import etree
import yaml
import logging
import logging.config

with open('logging.yaml') as fobj:
    logging.config.dictConfig(yaml.load(fobj))



logger = logging.getLogger(__name__)

logger.info("Starting parse")
tree = etree.parse('./iTunes Music Library.xml')
root = tree.getroot()

class Tracks:
    def __init__(self, track_node):
        self._track_node = track_node

    def _int_prop(self, key):
        return int(self._track_node.xpath(f"./key[.='{key}']/following-sibling::integer")[0].text)

    def _str_prop(self, key):
        return self._track_node.xpath(f"./key[.='{key}']/following-sibling::string")[0].text

    @property
    def track_id(self):
        return self._int_prop('Track ID')

    @property
    def size(self):
        return self._int_prop('Size')
    
    @property
    def name(self):
        return self._str_prop('Name')

    def __str__(self):
        return f"{self.track_id} {self.name}"


def get_tracks():
    # There is only one tag here
    top_dict = root[0]
    tracks_value_dict = top_dict.xpath("./key[.='Tracks']/following-sibling::dict")[0]
    print(tracks_value_dict)
    tracks_dicts=tracks_value_dict.xpath("./dict")
    t = Tracks(tracks_dicts[0])
    print(t)
        

get_tracks()


logger.info("Done")
