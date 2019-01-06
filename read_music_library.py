#!/usr/bin/env python3
from lxml import etree
import yaml
import logging
import logging.config
import dateutil.parser

with open('logging.yaml') as fobj:
    logging.config.dictConfig(yaml.load(fobj))



logger = logging.getLogger(__name__)

logger.info("Starting parse")
tree = etree.parse('./iTunes Music Library.xml')
root = tree.getroot()

class PlistInterface:
    def __init__(self, node):
        self._node = node

    @classmethod
    def int_prop_from_node(klass, key, node):
        return int(node.xpath(f"./key[.='{key}']/following-sibling::integer")[0].text)

    @classmethod
    def str_prop_from_node(self, key, node):
        return node.xpath(f"./key[.='{key}']/following-sibling::string")[0].text

    @classmethod
    def date_prop_from_node(self, key, node):
        return dateutil.parser.parse(node.xpath(f"./key[.='{key}']/following-sibling::date")[0].text)

    @classmethod
    def bool_prop_from_node(self, key):
        # This returns true only if the key exists AND the key is "true", else false (inc. None key)
        if (len(node.xpath(f"./key[.='{key}']/following-sibling::true") >= 1)):
            return true
        return false

    def _int_prop(self, key):
        return PlistInterface.int_prop_from_node(key, self._node)

    def _str_prop(self, key):
        return PlistInterface.str_prop_from_node(key, self._node)

    def _date_prop(self, key):
        return PlistInterface.date_prop_from_node(key, self._node)

    def _bool_prop(self, key):
        return PlistInterface.bool_prop_from_node(key, self._node)






class Tracks(PlistInterface):

    @classmethod
    def find_by_id(klass, song_id):
        top_dict = root[0]
        track_dict = top_dict.xpath(f"./key[.='Tracks']/following-sibling::dict/key[.='{song_id}']/following-sibling::dict")[0]
        return Tracks(track_dict)

    def __init__(self, node):
        super(Tracks, self).__init__(node)

    @property
    def track_id(self):
        return self._int_prop('Track ID')

    @property
    def size(self):
        return self._int_prop('Size')
                        
    @property
    def total_time(self):
        return self._int_prop('Total Time')
			
    @property
    def track_number(self):
        return self._int_prop('Track Number') 
			
    @property
    def year(self):
        return self._int_prop('Year')
			
    @property
    def date_modified(self):
        return self._date_prop('Date Modified')
			
    @property
    def date_added(self):
        return self._date_prop('Date Added')
			
    @property
    def bit_rate(self):
        return self._int_prop('Bit Rate')
			
    @property
    def sample_rate(self):
        return self._int_prop('Sample Rate')
			
    @property
    def play_count(self):
        return self._int_prop('Play Count')
			
    @property
    def play_date(self):
        return self._date_prop('Play Date')
			
    @property
    def play_date_utc(self):
        return self._date_prop('Play Date UTC')
			
    @property
    def rating(self):
        return self._int_prop('Rating')
			
    @property
    def album_rating(self):
        return self._int_prop('Album Rating')
			
    @property
    def album_rating_computed(self):
        return self._int_prop('Album Rating Computed')
			
    @property
    def persistent_id(self):
        return self._str_prop('Persistent ID')
			
    @property
    def track_type(self):
        return self._str_prop('Track Type')
			
    @property
    def file_folder_count(self):
        return self._int_prop('File Folder Count')
			
    @property
    def library_folder_count(self):
        return self._int_prop('Library Folder Count')
			
    @property
    def name(self):
        return self._str_prop('Name')
			
    @property
    def artist(self):
        return self._str_prop('Artist')
			
    @property
    def composer(self):
        return self._str_prop('Composer')
			
    @property
    def album(self):
        return self._str_prop('Album')
			
    @property
    def genre(self):
        return self._str_prop('Genre')
			
    @property
    def kind(self):
        return self._str_prop('Kind')
			
    @property
    def location(self):
        return self._str_prop('Location')

    def __str__(self):
        return f"{self.track_id} {self.name}"




class Playlists(PlistInterface):
    def __init__(self, node):
        super(Playlists, self).__init__(node)

    def playlist_items(self):
        pi_nodes =  self._node.xpath("./key[.='Playlist Items']/following-sibling::array/dict")
        return [Tracks.find_by_id(PlistInterface.int_prop_from_node('Track ID', node)) for node in pi_nodes]



    @property
    def master(self):
        return self._bool_prop('Master')
			
    @property
    def playlist_id(self):
        return self._int_prop('Playlist ID')
			
    @property
    def playlist_persistent_id(self):
        return self._str_prop('Playlist Persistent ID')
			
    @property
    def all_items(self):
        return self._bool_prop('All Items')
			
    @property
    def visible(self):
        return self._int_prop('Visible')
			
    @property
    def name(self):
        return self._str_prop('Name')

    def __str__(self):
        return f"{self.playlist_id} {self.name}"



def get_tracks():
    # There is only one tag here
    top_dict = root[0]
    # FIRST track. We can iterate.
    tracks_value_dict = top_dict.xpath("./key[.='Tracks']/following-sibling::dict/dict")[0]
    t = Tracks(tracks_value_dict)
    print(t)

def get_playlists():
    top_dict = root[0]
    # FIRST playlist.
    playlists_value_dict = top_dict.xpath("./key[.='Playlists']/following-sibling::array/dict")[10]
    p = Playlists(playlists_value_dict)
    pi = p.playlist_items()
    [print(song) for song in pi]

        

#get_tracks()
get_playlists()

#print(Tracks.find_by_id("2865"))

logger.info("Done")
