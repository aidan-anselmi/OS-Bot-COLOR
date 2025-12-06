

"""
commision
set mould
    plugin should make it so that top item is always the mould we want
    Tips -> Blades -> Forte
get ingots
fill crucible
    "What metal would you like to add?"
    steel -> 3
    "You add"
    mithril -> 4
pour
pick up mould

loop while we cant find cyan tag
    if green -> continue 
    if orange -> wait if close - click if far
    if red -> click on green or cyan or whatever
    if purple -> click on it 

hand in sword -> press space
recieve another commission -> press 1
"""

import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject, Rectangle
import random
import math
from utilities.sprite_scraper import SpriteScraper, ImageType
import utilities.imagesearch as imsearch
import pyautogui as pag
from pathlib import Path
import utilities.runelite_cv as rcv
import keyboard
import utilities.ocr as ocr

class GiantsFoundry(OSRSBot):
    def __init__(self):
        bot_title = "Giants Foundry"
        description = (
            """
            Checklist:
            - empty inventory
            - zoomed all the way out
            - facing north and slightly down

            """
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 175

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)

    def create_options(self):
        return

    def save_options(self, options: dict):
        self.options_set = True
        return 
    
    def scrape(self):
        scraper = SpriteScraper()

        # set destination directory to src/images/bot/items (project-relative)
        dest_dir = Path(__file__).resolve().parents[2].joinpath("images", "bot", "items")
        # make sure directory exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        search_string = "Mithril ingot, Steel ingot"
        # search_string = "Deposit Inventory"
        image_type = ImageType.BANK
        destination = dest_dir

        self.path = scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)
        return 
    
    def main_loop(self):    
        self.log_msg("Selecting inventory...")
        #pag.press('f2')
        #self.scrape()

        self.bank_color = clr.PINK
        self.active_station_color = clr.GREEN
        self.warning_station_color = clr.ORANGE
        self.bad_station_color = clr.RED
        self.bonus_color = clr.PURPLE
        self.mould_text_color = clr.BLUE

        self.set_mould()
        return 
    
        # Main loop
        # start_time = time.time()
        # end_time = self.running_time * 60
        # self.errors = 0
        # while time.time() - start_time < end_time and self.errors < 10:
        #     # mine until we have "full pay dirt"
        #     self.make_sword()

    def set_mould(self):
        rects = ocr.find_text(["Tips", "Blades", "Forte"], self.win.game_view, ocr.PLAIN_12, clr.OFF_ORANGE)
        if not rects:
            self.log_msg("No text found when setting mould")
            return False
        if len(rects) != 3:
            self.log_msg(f"Expected 3 text rects when setting mould, found {len(rects)}")
            return False

        tab_selects = 0
        for rect in rects:
            if self.find_click_rectangle(rect, "View", color=clr.OFF_WHITE):
                tab_selects += 1
            self.take_break(min_seconds=0, max_seconds=.3)

            text_rect = ocr.extract_text_rectangle(self.win.game_view, ocr.PLAIN_12, self.mould_text_color)
            if not text_rect or not self.find_click_rectangle(text_rect, "Select", color=clr.OFF_WHITE):
                self.log_msg("Failed to select mould")
                return False
            self.take_break(min_seconds=0, max_seconds=.3)

        if tab_selects >= 2:
            self.log_msg(f"Expected to click 2 tab selects when setting mould, clicked {tab_selects}")
            return False
        pag.press('esc')
        return True

    def make_sword(self):
        return
    
"""
commision
set mould
    plugin should make it so that top item is always the mould we want
    Tips -> Blades -> Forte
get ingots
fill crucible
    "What metal would you like to add?"
    steel -> 3
    "You add"
    mithril -> 4
pour
pick up mould

loop while we cant find cyan tag
    if green -> continue 
    if orange -> wait if close - click if far
    if red -> click on green or cyan or whatever
    if purple -> click on it 

hand in sword -> press space
recieve another commission -> press 1
"""