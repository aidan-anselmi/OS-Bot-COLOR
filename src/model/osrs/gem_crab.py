from curses import COLOR_CYAN
import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.imagesearch as imsearch
from utilities.sprite_scraper import SpriteScraper, ImageType
from pynput.keyboard import Key, Controller
import random


class OSRSGemCrabTrainer(OSRSBot):
    def __init__(self):
        bot_title = "gem crab"
        description = "fights gem crab"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120
        self.errors = 0

        self.crab_color = clr.CYAN
        self.cave_color = clr.PINK
        self.landing_pad_color = clr.GREEN

        self.time_multiplier = random.uniform(0.5, 2)

    
    def save_options(self, options: dict):
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):    
        start_time = time.time()
        end_time = self.running_time * 60

        self.click_cave()
        while time.time() - start_time < end_time and self.errors < 10:
            if self.find_crab():
                if random.uniform(0, 1) < .15:
                    self.click_landing_pad()
                self.click_crab()
                self.wait_for_kill()
            else:
                self.click_cave()
                if not self.find_crab():
                    self.click_landing_pad()

            self.log_msg(str((time.time() - start_time) / self.running_time) + "%\ done")

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.stop()
        return 

    def click_crab(self):
        res = self.find_click_tag(self.crab_color, "Attack", clr.OFF_WHITE)
        if not res:
            self.errors += 1
            self.log_msg("could not find click crab")
        self.take_break(min_seconds=1, max_seconds=2, fancy=True)
        return res

    def click_landing_pad(self):
        res = self.find_click_tag(self.landing_pad_color, "Walk here", clr.OFF_WHITE)
        if not res:
            self.errors += 1
            self.log_msg("could not find click landing pad")
        self.take_break(min_seconds=.5, max_seconds=1.5, fancy=True)
        return res

    def click_cave(self):
        res = self.find_click_tag(self.cave_color, "Crawl-through", clr.OFF_WHITE)
        if not res:
            self.errors += 1
            self.log_msg("could not find click cave")
        self.take_break(min_seconds=2, max_seconds=3, fancy=True)
        return res

    def find_crab(self):
        tag = self.loop_find_tag(self.crab_color)
        if not tag:
            return False
        return True

    def wait_for_kill(self):
        # small chance to click crab. 
        base_cycles_inverse = (10*60 / 15)**-1
        reclick_chance = .20 * base_cycles_inverse
        move_mouse_chance = 1 * base_cycles_inverse

        while self.find_crab():
            self.take_break(min_seconds=1, max_seconds=30, fancy=True)

            if random.uniform(0, 1) < reclick_chance:
                self.click_crab()
            if random.uniform(0, 1) < move_mouse_chance:
                self.move_mouse_random_point()
            
        return 