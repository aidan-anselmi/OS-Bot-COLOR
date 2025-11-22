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

class TemplteTrekker(OSRSBot):
    def __init__(self):
        bot_title = "Woodcutter"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)

        self.keyboard = Controller()

    def create_options(self):
        return
    
    def main_loop(self):
        start_time = time.time()
        end_time = self.running_time * 60
        errors = 0

        while time.time() - start_time < end_time and errors < 10:
            continue 
        return
    
    def start_trek(self):
        self.find_click_tag(clr.CYAN, "Escort", clr.OFF_WHITE)
        self.keyboard.press(Key.space)
        self.find_click_image("Path_to_route_one")
        return
    
    def handle_encounter(self):
        # bog event
        if self.loop_find_tag(clr.YELLOW):
            return self.bog()
        if self.loop_find_tag(clr.RED):
            return self.log_event()
        if self.loop_find_tag(clr.PINK):
            return self.enemy_encounter()
        return 
    
    def log_event(self):
        # red to attack zombies OR cut logs 
        # blue to repair bridge 
        # yellow to cross 
        # pink to leave encounter
        return
    
    def log_event_tree(self):
        return
    
    def log_event_zombie(self):
        return 
    
    def repair_and_cross_bridge(self, repair_item):
        return 
    
    def enemy_encounter(self):
        # pink to leave
        # green to walk 

        return 
    
    def bog(self):
        # yellow to leave
        # after teleport home
        return 
    
    def home(self):
        # teleport home spell
        # pink to teleporter
        # green tiles to get closer to NPCs
        return 
    
    def open_loot(self):
        # find images in slots and open
        # click bowstrings
        # click claim
        # continue until all open 
        return