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

class SandMiner(OSRSBot):
    def __init__(self):
        bot_title = "Sand Miner"
        description = (
            "This bot mines sand. Position your character near some sand, tag it, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 172

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)
        
        self.tree_color = clr.PINK
        self.bank_color = clr.BLUE

    def create_options(self):
        return

    def save_options(self, options: dict):
        self.options_set = True
        return 

    def main_loop(self):
        self.log_msg("Selecting inventory...")
        pag.press('f2')

        
        rock_clr = clr.PINK
        self.deposit_color = clr.GREEN

        self.empty_slot_clr_27 = pag.pixel(*self.win.inventory_slots[-1].get_center())
        self.inventory_pixel_map = {}
        for i in range(len(self.win.inventory_slots)):
            self.inventory_pixel_map[i] = pag.pixel(*self.win.inventory_slots[i].get_center())
        self.log_msg(f"{self.inventory_pixel_map}")

        start = 11
        i = start

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        errors = 0
        while time.time() - start_time < end_time and errors < 10:
            while not self.full_inventory():
                self.find_click_tag_with_missclick(rock_clr, "Mine", clr.OFF_WHITE, probability=0.05)
                for _ in range(40):
                    if not self.slot_empty(i):
                        i += 1
                        break
                    time.sleep(0.1)
            if not self.deposit_sand():
                errors += 1
                if not self.deposit_sand():
                    return
            i = start

    def deposit_sand(self):
        for _ in range(3):
            if self.find_click_tag(self.deposit_color, "Deposit", clr.OFF_WHITE):
                for _ in range(10):
                    if self.slot_empty(27):
                        return True
                    time.sleep(1)
        return False
            
    def full_inventory(self) -> bool:
        if pag.pixel(*self.win.inventory_slots[-1].get_center()) != self.empty_slot_clr_27:
            return True
        return False
    
    def slot_empty(self, slot_index: int) -> bool:
        if pag.pixel(*self.win.inventory_slots[slot_index].get_center()) == self.inventory_pixel_map[slot_index]:
            return True
        return False
