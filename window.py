import urllib.parse
import subprocess
import requests
import platform
import ctypes
import os

from screeninfo import get_monitors
from bs4 import BeautifulSoup
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.actionbar import ActionItem


class ActionTextInput(TextInput, ActionItem):
    pass


class WallpaperUtil(App):
    def __init__(self):
        super().__init__()
        self.general = True
        self.anime = True
        self.people = True
        self.sfw = True
        self.sketchy = False
        self.nsfw = False
        self.order = 'descending'
        self.size = 'exact'

        # if not three digits long add leading zeros till it is
        # do this after adding them together as ints, then convert
        # to a string

        self.categories = {
            'general': 100,
            'anime': 10,
            'people': 1
        }

        self.purity_level = {
            'sfw': 100,
            'sketchy': 10,
            'nsfw': 1
        }

        self.sorting = {
            'date': 'date_added',
            'relevance': 'relevance',
            'random': 'random',
            'views': 'views',
            'favorites': 'favorites'
        }

        self.ordering = {
            'descending': 'desc',
            'ascending': 'asc'
        }

    def do_search(self, terms):
        print(terms)
        self.root.ids.search.text = ''

    def cycle_sorting(self):
        current = self.root.ids.sorting.text.lower()
        is_next = False
        for i, sort in enumerate(self.sorting):
            if is_next is True and sort != current:
                self.root.ids.sorting.text = sort.title()
                break
            if sort == current:
                is_next = True
            if i == 4:
                self.root.ids.sorting.text = 'Date'
                break

    def toggle_order(self):
        if self.order == 'descending':
            self.root.ids.order.icon = 'icons/icons8-up-48.png'
            self.order = 'ascending'
        else:
            self.root.ids.order.icon = 'icons/icons8-down-arrow-48.png'
            self.order = 'descending'

    def toggle_size(self):
        if self.size == 'exact':
            self.size = 'any'
            self.root.ids.size.text = self.size.title()
        else:
            self.size = 'exact'
            self.root.ids.size.text = self.size.title()

    @staticmethod
    def leading_zeros(num1, num2=0, num3=0):
        added_nums = str(num1 + num2 + num3)
        if len(added_nums) < 3:
            final_num = f'{"0" * (3 - len(added_nums))}{added_nums}'
        else:
            final_num = added_nums
        return final_num

    def new_wallpaper(self):
        if self.size == 'exact':
            screens = get_monitors()
            resolution = f"{screens[0].width}x{screens[0].height}"
        else:
            resolution = ''

        base_url = "https://alpha.wallhaven.cc/"
        image_server = "https://wallpapers.wallhaven.cc/"

        if self.sfw is True and self.sketchy is True and self.nsfw is True:
            purity = '111'
        elif self.sfw is True and self.sketchy is True and self.nsfw is False:
            purity = '110'
        elif self.sfw is True and self.sketchy is False and self.nsfw is False:
            purity = '100'
        elif self.sfw is False and self.sketchy is True and self.nsfw is True:
            purity = '011'
        elif self.sfw is False and self.sketchy is False and self.nsfw is True:
            purity = '001'
        elif self.sfw is False and self.sketchy is True and self.nsfw is False:
            purity = '010'
        elif self.sfw is True and self.sketchy is False and self.nsfw is True:
            purity = '101'
        else:
            purity = '000'

        if self.general is True and self.anime is True and self.people is True:
            category = '111'
        elif self.general is True and self.anime is True and self.people is False:
            category = '110'
        elif self.general is True and self.anime is False and self.people is False:
            category = '100'
        elif self.general is False and self.anime is True and self.people is True:
            category = '011'
        elif self.general is False and self.anime is False and self.people is True:
            category = '001'
        elif self.general is False and self.anime is True and self.people is False:
            category = '010'
        elif self.general is True and self.anime is False and self.people is True:
            category = '101'
        else:
            category = '000'

        options = {
            'categories': category,
            'purity': purity,
            'resolutions': resolution,
            # Todo: Add a button for this
            'sorting': self.sorting[self.root.ids.sorting.text.lower()],
            # Todo: Add a button for this
            'order': self.ordering[self.order]
        }
        url = f"{base_url}search?q="
        if self.root.ids.search.text:
            if " " in self.root.ids.search.text:
                term = self.root.ids.search.text.replace(" ", "+")
            else:
                term = self.root.ids.search.text
            url = f"{url}{term}&search_image=&"
        else:
            url = f"{url}&search_image=&"
        url = url + urllib.parse.urlencode(options)

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        thumb_list = soup.find("section", {"class": "thumb-listing-page"}).ul

        if thumb_list:
            wallpaper_id = thumb_list.find("figure", {"class": "thumb"})['data-wallpaper-id']
            wallpaper_url = f"{image_server}wallpapers/full/wallhaven-{wallpaper_id}.jpg"
            wallpaper_response = requests.get(wallpaper_url)

            # Images can be in one of three formats, its not possible
            # to find out which ahead of time so if we reach a 404 then
            # retry with a different file extension.

            c = 0
            extensions = ['png', 'jpg', 'gif']
            while wallpaper_response.status_code == 404:
                wallpaper_url = f"{image_server}wallpapers/full/wallhaven-{wallpaper_id}.{extensions[c]}"
                wallpaper_response = requests.get(wallpaper_url)
                if wallpaper_response.status_code == 404:
                    c += 1

            with open(f"wallpaper.{extensions[c]}", "wb") as file:
                file.write(wallpaper_response.content)

    @staticmethod
    def apply_wallpaper():
        here = os.path.dirname(os.path.realpath(__file__))
        if platform.system() == 'Windows':
            ctypes.windll.user32.SystemParametersInfoW(20, 1, f"{here}\wallpaper.png", 2)
        elif platform.system() == 'Linux':
            print("Add wallpaper setting utility to settings!")
        elif platform.system() == 'Darwin':
            subprocess.Popen(['osascript',
                              '-e',
                              f'tell application "Finder" to set desktop picture to POSIX file "{here}\wallpaper.png"'])


if __name__ == '__main__':
    WallpaperUtil().run()
