#!/usr/bin/env python3
from lxml import etree
import yaml
import logging
import logging.config
import dateutil.parser
import curses
from curses import wrapper

with open('logging.yaml') as fobj:
    logging.config.dictConfig(yaml.load(fobj))



logger = logging.getLogger("rml")
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


class CursesWinAbs:
    def __init__(self, parent, win):
        self._parent = parent
        self._win = win
        self._children = []

    def add_child(self, klass, height, width, y, x):
        win = curses.newwin(height, width, y, x)
        child = klass(self, win)
        self._children.append(child)
        return child

    def redraw_recursive(self):
        self.draw()
        [child.redraw_recursive() for child in self._children]

    def refresh_recursive(self):
        self._win.refresh()
        [child.refresh_recursive() for child in self._children]

class MainWin(CursesWinAbs):
    def __init__(self, win):
        super(MainWin, self).__init__(None, win)

    def draw(self):
        self._win.addstr(0, 0, "Main Window")

class Menu(CursesWinAbs):

    def draw(self):
        for i in range(0, curses.COLS):
            self._win.addch(0, i, '=', curses.A_REVERSE)
        self._win.addstr(0, 0, "Hotkeys:", curses.A_REVERSE)

class NavigableMenu(CursesWinAbs):
    def __init__(self, parent, win):
        super(NavigableMenu, self).__init__(None, win)
        self._options = []

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def draw(self):
        self._win.addstr(0, 0, "Please select an option:")
        for i in range(0, len(self._options)):
            self._win.addstr(i + 1, 0, f"{i}: ", curses.A_BOLD | curses.color_pair(1))
            self._win.addstr(i + 1, 3, f"{str(self._options[i])}")

class Keymapping(CursesWinAbs):
    def __init__(self, stdscr):
        self._scr = stdscr
        self._mapping = {}

    def register_callback(self, char, cb):
        self._mapping[char] = cb

    def listen(self):
        key = self._scr.getkey()
        if key in self._mapping:
            logger.debug(f"Key {key} pressed")

def main(stdscr):
    stdscr.clear()

    # Init pallette
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)

    main_win = MainWin(stdscr)
    HEIGHT=3
    menu = main_win.add_child(Menu, HEIGHT, curses.COLS, curses.LINES - HEIGHT, 0)
    HEIGHT=curses.LINES - HEIGHT - 1
    nav = main_win.add_child(NavigableMenu, HEIGHT, curses.COLS, 1, 0)
    nav.options = ["List albums", "List songs", "Search albums by name", "Search songs by name"]
    mapping = Keymapping(stdscr)
    mapping.register_callback('0', None)
    main_win.redraw_recursive()
    main_win.refresh_recursive()
    mapping.listen()

    #get_playlists()

curses.wrapper(main)

logger.info("Done")
