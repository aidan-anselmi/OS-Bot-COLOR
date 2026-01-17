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
import cv2
import utilities.ocr as ocr

class SeaweedAlc(OSRSBot):
    def __init__(self):
        bot_title = "SeaweedAlc"
        description = (
            """
            Checklist:
            - empty inventory
            - zoomed all the way out
            - facing north and slightly down

            """
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 119

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)

    def create_options(self):
        return

    def save_options(self, options: dict):
        self.options_set = True
        return 

    def main_loop(self):    
        self.log_msg("Starting seaweed alching...")
        pag.press('f4')

        text = ocr.extract_text(self.win.game_view, font=ocr.PLAIN_11, color=clr.PURPLE)
        self.log_msg(f"OCR purple text: {text}")
        return

        self.desposit_all_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        self.close_bank_img = imsearch.BOT_IMAGES.joinpath("bank", "close_bank.png")

        self.inventory_pixel_map = {}
        for i in range(len(self.win.inventory_slots)):
            self.inventory_pixel_map[i] = pag.pixel(*self.win.inventory_slots[i].get_center())

        self.distracted_citizen_tile_color = clr.GREEN
        self.distracted_citizen_clickbox_color = clr.CYAN

        self.alc_intersect = self.win.spellbook_normal[35].intersect(self.win.inventory_slots[12])
        if not self.alc_intersect:
            self.log_msg("ERROR: High alchemy spell does not intersect inventory slot 12!")
            return
        
        xp = self.get_total_xp()
        xp_timestamp = time.time()
        pag.press('f4')
        self.take_break(min_seconds=.1, max_seconds=.5, fancy=True)
        self.find_click_rectangle(self.alc_intersect, "Cast", clr.OFF_WHITE)
        while True:
            cur_xp = self.get_total_xp()
            if cur_xp != -1 and cur_xp != xp:
                xp = cur_xp
                xp_timestamp = time.time()

            if time.time() - xp_timestamp > 5 * 60:
                self.log_msg("did not get xp for 5mins, retrying")
                pag.press('f4')
                time.sleep(.2)
                self.find_click_rectangle(self.alc_intersect, "Cast", clr.OFF_WHITE)
                time.sleep(.2)
            if time.time() - xp_timestamp > 10 * 60:
                self.log_msg("not getting xp, logging out")
                return
                

            self.take_break(min_seconds=.3, max_seconds=.8, fancy=True)
            self.mouse.click()
            self.take_break(min_seconds=.3, max_seconds=.8, fancy=True)
            if rd.random_chance(0.005):
                if rd.random_chance(0.1):
                    self.take_break(min_seconds=30, max_seconds=200)
                else:
                    self.take_break(min_seconds=5, max_seconds=30)
            else:
                self.mouse.click()
        return 

    def pickup_seaweed(self):
        self.pick_up_loot(["Seaweed spore"])
        return
    
    def alc(self):
        return
    
    

