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
    

    
    def start_trek(self):
        self.find_click_tag(clr.CYAN, "Escort", clr.OFF_WHITE)

        return
    
    def route_encounter():
        return 
    
    def log_event():
        # red to attack zombies OR cut logs 
        # blue to repair bridge 
        # yellow to cross 
        # pink to leave encounter
        return
    
    def encounter():
        # pink to leave
        # yellow to walk 
        return 
    
    def bog():
        # yellow to leave
        # after teleport home
        return 
    
    def home():
        # teleport home spell
        # pink to teleporter
        # green tiles to get closer to NPCs
        return 