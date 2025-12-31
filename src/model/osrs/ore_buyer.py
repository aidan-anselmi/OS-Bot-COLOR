import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject
import random
from utilities.sprite_scraper import SpriteScraper, ImageType
import utilities.imagesearch as imsearch
import pyautogui as pag
from pynput.keyboard import Key, Controller
import utilities.ocr as ocr
import math
from pathlib import Path

class OreBuyer(OSRSBot):
    def __init__(self):
        bot_title = "Woodcutter"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 60

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)

        self.keyboard = Controller()

    def create_options(self):
        return
    
    def scrape(self):
        scraper = SpriteScraper()

        # set destination directory to src/images/bot/items (project-relative)
        dest_dir = Path(__file__).resolve().parents[2].joinpath("images", "bot", "items")
        # make sure directory exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        search_string = "Iron ore, Coal"
        # search_string = "Deposit Inventory"
        image_type = ImageType.BANK
        destination = dest_dir

        self.path = scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)
        return 
    

    def save_options(self, options: dict):
        self.options_set = True
        return 
    
    def main_loop(self):
        

        start_time = time.time()
        end_time = self.running_time * 60
        self.errors = 0
        pag.press("f2")
        self.scrape()
        time.sleep(.3)

        self.empty_slot_clr_27 = pag.pixel(*self.win.inventory_slots[-1].get_center())
        self.bank_color = clr.PINK
        self.ore_seller_color = clr.ORANGE

        self.coal_in_stock = True
        self.iron_in_stock = True

        while time.time() - start_time < end_time and self.errors < 10:
            if self.full_inventory():
                pag.press("f2")

            if not self.find_click_tag(self.ore_seller_color, mouseover_text="Trade", color=clr.OFF_WHITE):
                time.sleep(1)
                continue

            # buy iron
            self.sleep_until_not_moving()
            if coal_rect := self.loop_find_image(image=self.path.joinpath("Coal_bank.png"), rect=self.win.game_view):
                if self.find_click_rectangle(coal_rect, mouseover_text="Buy", color=clr.OFF_WHITE):
                    self.take_break(min_seconds=.3, max_seconds=1)
                    pag.press(keys="esc")
                    self.take_break(min_seconds=.3, max_seconds=1)
                    if not self.full_inventory():
                        self.coal_in_stock = False

                    self.find_click_rectangle(self.win.inventory_slots[1], mouseover_text="Fill", color=clr.OFF_WHITE)
            
            # buy coal
            if self.find_click_tag(self.ore_seller_color, mouseover_text="Trade", color=clr.OFF_WHITE):
                if iron_rect := self.loop_find_image(image=self.path.joinpath("Iron_ore_bank.png"), rect=self.win.game_view): 
                    if self.find_click_rectangle(iron_rect, mouseover_text="Buy", color=clr.OFF_WHITE):
                        self.take_break(min_seconds=.3, max_seconds=1)
                        pag.press(keys="esc")
                        self.take_break(min_seconds=.3, max_seconds=1)
                        if not self.full_inventory():
                            self.iron_in_stock = False
            
            # bank
            self.find_click_tag(self.bank_color, mouseover_text="Use", color=clr.OFF_WHITE)
            self.wait_till_bank_open()
            self.find_click_rectangle(self.win.inventory_slots[1], mouseover_text="Empty", color=clr.OFF_WHITE)
            self.find_click_rectangle(self.win.inventory_slots[2], mouseover_text="Deposit", color=clr.OFF_WHITE)
            self.take_break(min_seconds=.3, max_seconds=1)
            pag.press(keys="esc")
            self.take_break(min_seconds=.3, max_seconds=1)

            self.turn_on_run()
            
            # hop
            if not self.coal_in_stock:
                self.hop()
            if not self.iron_in_stock:
                self.hop()
        return 
    
    def sleep_until_not_moving(self, color=clr.PINK):
        time.sleep(1)
        while self.loop_find_tag(color, loops=3):
            prev = self.loop_find_tag(color, loops=1)
            time.sleep(.2)
            curr = self.loop_find_tag(color, loops=1)
            if prev and curr and math.dist(prev.get_center(), curr.get_center()) < 2:
                break
        time.sleep(.3)
        return
    
    def full_inventory(self) -> bool:
        return pag.pixel(*self.win.inventory_slots[-1].get_center()) != self.empty_slot_clr_27
    
    def turn_on_run(self):
        if self.get_run_energy() == 100 and rd.random_chance(0.8):
            self.find_click_rectangle(self.win.run_orb, "Toggle Run", color=clr.OFF_WHITE)
            return True
        return False
    
    def hop(self):
        pag.keyDown('shift')
        time.sleep(0.1)
        pag.press('pageup')
        pag.keyUp('shift')
        if self.wait_till_interface_text("World", font=ocr.QUILL_8, color=clr.BLACK, max_wait=10):
            self.log_msg("Ran into forbidden world, ending")
            self.errors += 10
        pag.press("f2")
        self.iron_in_stock = True
        self.coal_in_stock = True
        return
        