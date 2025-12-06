

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

        
    
        start_time = time.time()
        end_time = self.running_time * 60
        self.errors = 0
        while time.time() - start_time < end_time and self.errors < 10:
            self.get_commission()
            self.take_break(min_seconds=0, max_seconds=.5)
            self.set_mould()
            self.get_bars()
            self.add_bars_to_crucible()

            self.make_sword()

    def get_commission(self):
        kovac = self.loop_find_tag(clr.CYAN)
        if not kovac:
            self.log_msg("Could not find Kovac to get commission")
            return False
        self.mouse.move_to(kovac.random_point())
        self.mouse.right_click()
        if take_text := ocr.find_text(
                "Commission",
                self.win.game_view,
                ocr.BOLD_12,
                clr.WHITE,
            ):
            self.mouse.move_to(take_text[0].random_point(), mouseSpeed="medium")
            self.mouse.click()
            return True
        return False

    def set_mould(self):
        blade_parts = ["Forte", "Blades", "Tips"]
        if rd.random_chance(0.4):
            blade_parts.reverse()

        tab_selects = 0
        for blade_part in ["Tips", "Blades", "Forte"]:
            tab_rects = ocr.find_text(blade_part, self.win.game_view, ocr.PLAIN_12, clr.OFF_ORANGE)
            if not tab_rects:
                self.log_msg("No text found when setting mould")
                return False
            if len(tab_rects) != 1:
                self.log_msg(f"Expected 1 text rect when selecting tab, found {len(tab_rects)}")
                return False
            if self.find_click_rectangle(tab_rects[0], "View", color=clr.OFF_WHITE):
                tab_selects += 1

            search_texts = ["Saw Tip", "Gladius Point", "Serpent's Fang", "Medusa's Head", "Chopper Tip", "People Poker Point"]
            if blade_part == "Forte":
                search_texts = ["Serrated Forte", "Serpent Ricasso", "Medusa Ricasso", "Disarming Forte", "Gladius Ricasso", "Chopper Forte"]
            elif blade_part == "Blades":
                search_texts = ["Gladius Edge", "Stiletto Blade", "Medusa Blade", "Fish Blade", "Defenders Edge", "Saw Blade"]
            mould_rects = ocr.find_text(search_texts, self.win.game_view, ocr.BOLD_12, self.mould_text_color)
            if not mould_rects:
                self.log_msg("No text found when setting mould")
                return False
            if len(mould_rects) != 1:
                self.log_msg(f"Expected 1 text rect when setting mould, found {len(mould_rects)}")
                return False
            if not self.find_click_rectangle(mould_rects[0], "Select", color=clr.OFF_WHITE):
                self.log_msg("Failed to click mould when setting mould")
                return False

        if tab_selects < 2:
            self.log_msg(f"Expected to click 2 tab selects when setting mould, clicked {tab_selects}")
        pag.press('esc')
        return True
    
    def get_bars(self):
        self.find_click_tag(self.bank_color, "Use", color=clr.OFF_WHITE)
        self.wait_till_bank_open()
        self.find_click_image(self.path.joinpath("Mithril_ingot_bank.png"))
        self.take_break(min_seconds=0.1, max_seconds=0.5)
        self.find_click_image(self.path.joinpath("Steel_ingot_bank.png"))
        self.take_break(min_seconds=0.1, max_seconds=0.5)
        pag.press('esc')
        return
    
    def add_bars_to_crucible(self):
        order = ["3", "4"]
        if rd.random_chance(0.2):
            order.reverse()

        for button in order:
            self.find_click_tag(self.active_station_color, "Fill", color=clr.OFF_WHITE)
            self.wait_till_interface_text("What metal")
            pag.press(button)
            self.wait_till_interface_text("You add")
        return

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