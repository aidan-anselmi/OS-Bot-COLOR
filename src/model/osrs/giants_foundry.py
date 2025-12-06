

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

        search_string = "Mithril bar, Steel bar"
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
        self.scrape()

        self.bank_color = clr.PINK
        self.active_station_color = clr.GREEN
        self.warning_station_color = clr.ORANGE
        self.bad_station_color = clr.RED
        self.bonus_color = clr.PURPLE
        self.mould_text_color = clr.BLUE
        self.general_color = clr.BLUE

        
    
        start_time = time.time()
        end_time = self.running_time * 60
        self.errors = 0
        while time.time() - start_time < end_time and self.errors < 10:
            self.setup_sword()
            self.make_sword()
            self.hand_in_sword()

    def setup_sword(self):
        #self.get_commission()
        self.take_break(min_seconds=0, max_seconds=.5)
        self.set_mould()
        self.get_bars()
        self.add_bars_to_crucible()
        self.find_click_tag(self.active_station_color, "Pour", color=clr.OFF_WHITE)
        self.take_break(min_seconds=1, max_seconds=3)
        self.find_click_tag(self.general_color, "Pick-up", color=clr.OFF_WHITE)
        self.take_break(min_seconds=5.5, max_seconds=8)
        return

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
            time.sleep(3)
            return True
        self.log_msg("Could not find commission option when right clicking Kovac")
        return False

    def set_mould(self):
        if not self.find_click_tag(self.general_color, "Setup", color=clr.OFF_WHITE):
            self.log_msg("Failed to find and click setup station")
            return False
        time.sleep(4)

        blade_parts = ["Forte", "Blades", "Tips"]
        if rd.random_chance(0.4):
            blade_parts.reverse()

        tab_selects = 0
        for blade_part in blade_parts:
            if not self.select_tab(blade_part):
                self.log_msg(f"Failed to select {blade_part} tab when setting mould")
                return False

            search_texts = ["Saw Tip", "Gladius Point", "Serpent's Fang", "Medusa's Head", "Chopper Tip", "People Poker Point"]
            if blade_part == "Forte":
                search_texts = ["Serrated Forte", "Serpent Ricasso", "Medusa Ricasso", "Disarming Forte", "Gladius Ricasso", "Chopper Forte"]
            elif blade_part == "Blades":
                search_texts = ["Gladius Edge", "Stiletto Blade", "Medusa Blade", "Fish Blade", "Defenders Edge", "Saw Blade"]
            mould_rects = ocr.find_text(search_texts, self.win.game_view, ocr.BOLD_12, self.mould_text_color)
            if not mould_rects:
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
    
    def select_tab(self, tab_name: str):
        tab_name = tab_name.lower()
        path = imsearch.BOT_IMAGES.joinpath("giants_foundry", f"{tab_name}_large_selected.png")
        self.log_msg(f"Selecting tab {path}")
        if self.loop_find_image(path, self.win.game_view, loops=3):
            return True
        path = imsearch.BOT_IMAGES.joinpath("giants_foundry", f"{tab_name}_large_tab.png")
        if self.find_click_image(path, self.win.game_view, "View"):
            return True
        return False
    
    def get_bars(self):
        self.find_click_tag(self.bank_color, "Use", color=clr.OFF_WHITE)
        self.wait_till_bank_open()
        self.find_click_image(self.path.joinpath("Mithril_bar_bank.png"))
        self.take_break(min_seconds=0.1, max_seconds=0.5)
        self.find_click_image(self.path.joinpath("Steel_bar_bank.png"))
        self.take_break(min_seconds=0.1, max_seconds=0.5)
        pag.press('esc')
        return
    
    def add_bars_to_crucible(self):
        order = ["3", "4"]
        if rd.random_chance(0.2):
            order.reverse()

        for button in order:
            self.find_click_tag(self.general_color, "Fill", color=clr.OFF_WHITE)
            self.wait_till_interface_text("What metal")
            time.sleep(.2)
            pag.press(button)
            # TODO the font for this is off
            self.wait_till_interface_text("You add")
        return

    def make_sword(self):
        """
        loop while we cant find blue tag
            if green -> continue 
            if orange -> wait if close - click if far
            if red -> click on green or cyan or whatever
            if purple -> click on it 
        """
        while not self.loop_find_tag(self.general_color) and self.errors < 10:
            if rect := self.loop_find_tag(self.active_station_color, loops=1):
                self.mouse.move_to(rect.random_point())
                if self.mouseover_text(contains="Use", color=clr.OFF_WHITE) or self.mouseover_text(contains="Heat", color=clr.OFF_WHITE) or self.mouseover_text(contains="Cool", color=clr.OFF_WHITE):
                    self.mouse.click()
                    time.sleep(.2)
                    self.wait_until_tag_stops_moving(self.active_station_color)
                    self.wait_until_tag_moves(self.active_station_color)
                else:
                    self.log_msg("Active station found but mouseover text not correct, moving on")
                    time.sleep(.1)
            elif rect := self.loop_find_tag(self.bonus_color, loops=1):
                self.mouse.move_to(rect.random_point())
                if self.mouseover_text(contains="Use", color=clr.OFF_WHITE):
                    self.mouse.click()
                    time.sleep(.1)
                else:
                    self.log_msg("Bonus station found but mouseover text not correct, moving on")
                    time.sleep(.1)
            elif rect := self.loop_find_tag(self.warning_station_color, loops=1):
                distance = RuneLiteObject.distance_from_rect_center(rect)
                if distance < 100:
                    self.log_msg("Warning station close, waiting for it to be done")
                    self.wait_until_tag_moves(self.warning_station_color)
                    continue
                else:
                    self.log_msg("Clicking warning station as it is far away")
                    self.mouse.click()
                    time.sleep(.2)
                    self.wait_until_tag_stops_moving(self.warning_station_color)
                    self.wait_until_tag_moves(self.warning_station_color)
                    continue
        

        if self.errors < 10:
            self.log_msg("Sword made!")
        else:
            self.log_msg("Too many errors making sword, moving on")
        return
    
    def hand_in_sword(self):
        self.find_click_tag(self.general_color, "Hand-in", color=clr.OFF_WHITE)
        self.wait_until_tag_stops_moving(self.general_color)
        pag.hold('space')
        time.sleep(2)
        pag.press('1')
        return
    
    def has_tag_moved(self, tag: clr.Color) -> bool:
        if not self.tag_map:
            self.tag_map = {}
        initial_tag = self.loop_find_tag(tag)
        if not initial_tag:
            return True
        
        if not tag in self.tag_map:
            self.tag_map[tag] = initial_tag.get_center()
            return True
        if math.dist(self.tag_map[tag], initial_tag.get_center()) > 5:
            self.tag_map[tag] = initial_tag.get_center()
            return True
        return False
    
    def wait_until_tag_moves(self, tag: clr.Color, timeout: int = 30) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.has_tag_moved(tag):
                return True
            time.sleep(0.1)
        self.log_msg(f"Tag {tag} did not move within timeout")
        self.errors += 1
        return False
    
    def wait_until_tag_stops_moving(self, tag: clr.Color, timeout: int = 30) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.has_tag_moved(tag):
                return True
            time.sleep(0.1)
        self.log_msg(f"Tag {tag} did not stop moving within timeout")
        self.errors += 1
        return False
    
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

loop while we cant find blue tag
    if green -> continue 
    if orange -> wait if close - click if far
    if red -> click on green or cyan or whatever
    if purple -> click on it 

hand in sword -> press space
recieve another commission -> press 1


# read overlay for 
Stage 
heat 
Actions left 
"""