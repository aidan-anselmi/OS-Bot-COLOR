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

class ThieveAlc(OSRSBot):
    def __init__(self):
        bot_title = "ThieveAlc"
        description = (
            """
            Checklist:
            - empty inventory
            - zoomed all the way out
            - facing north and slightly down

            """
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)

    def create_options(self):
        return

    def save_options(self, options: dict):
        self.options_set = True
        return 

    def main_loop(self):    
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

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

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        self.errors = 0
        alcs = 0
        while time.time() - start_time < end_time and self.errors < 10:
            if self.hop_if_player_nearby():
                pag.press('f2')

            distracted_citizen_tile = self.loop_find_tag(self.distracted_citizen_tile_color, loops=5, sleep=0.02)
            if not distracted_citizen_tile:
                pag.press('f4')
                self.take_break(min_seconds=.2, max_seconds=.4, fancy=True)
                self.find_click_rectangle(self.alc_intersect, "Cast", clr.OFF_WHITE)
            while not distracted_citizen_tile:
                self.take_break(min_seconds=.1, max_seconds=.25, fancy=True)
                self.mouse.click()
                self.take_break(min_seconds=.1, max_seconds=.25, fancy=True)
                self.mouse.click()

                alcs += 1
                if alcs % 100 == 0:
                    self.log_msg(f"High alched {alcs} times so far...")
                
                distracted_citizen_tile = self.loop_find_tag(self.distracted_citizen_tile_color, loops=5, sleep=0.02)
                if not distracted_citizen_tile:
                    self.log_msg("No distracted citizen found, re-casting high alch...")
                else:
                    self.log_msg("Distracted citizen found, attempting to thieve...")

            self.thieve_citizen(distracted_citizen_tile)
                    
            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        return 
    
    def thieve_citizen(self, distracted_citizen_tile = None):
        if not distracted_citizen_tile:
            distracted_citizen_tile = self.loop_find_tag(self.distracted_citizen_tile_color)

        if distracted_citizen_tile:
            citizen = self.get_all_tagged_in_rect(distracted_citizen_tile, self.distracted_citizen_clickbox_color)
            if not citizen:
                self.log_msg("No citizen found in clickbox, retrying...")
                return self.thieve_citizen()
            if len(citizen) > 1:
                self.log_msg("ERROR Multiple citizens found in clickbox")
                return self.thieve_citizen()
            citizen = citizen[0]
            self.mouse.move_to(citizen.random_point())

            # clear spell
            if self.mouseover_text(contains="Cast", color=clr.OFF_WHITE):
                self.mouse.click()
                self.take_break(min_seconds=.1, max_seconds=.2)

            if not self.mouseover_text(contains="Pickpocket"):
                self.mouse.click()
                self.log_msg("Mouseover text not found, retrying...")
                return self.thieve_citizen()
            self.mouse.click()
            time.sleep(2)

            # wait until we stop thieving 
            xp = self.get_total_xp()
            if xp == -1:
                time.sleep(2)
                xp = self.get_total_xp()
            while self.get_total_xp() != -1 and self.get_total_xp() != xp:
                xp = self.get_total_xp()
                time.sleep(1)

            # open inventory with f2 and open pouch
            pag.press('f2')
            self.find_click_rectangle(self.win.inventory_slots[0], "Open-all", clr.OFF_WHITE)

            return True
        return False
    

