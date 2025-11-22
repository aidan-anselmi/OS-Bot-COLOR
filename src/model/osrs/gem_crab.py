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
        self.running_time = 131
        self.errors = 0

        self.crab_color = clr.CYAN
        self.cave_color = clr.PINK
        self.landing_pad_color = clr.GREEN

        self.time_multiplier = random.uniform(0.5, 2)

        self.cave_consec = 0

    def create_options(self):
        return

    def save_options(self, options: dict):
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):    
        start_time = time.time()
        end_time = self.running_time * 60

        while time.time() - start_time < end_time and self.errors < 10 and self.cave_consec < 3:
            if self.find_crab():
                if random.random() < 0.15:
                    self.click_landing_pad()
                    self.take_break(min_seconds=.5, max_seconds=1, fancy=True)
                self.click_crab()
                self.wait_for_kill()
            else:
                self.click_cave()
                if not self.find_crab():
                    self.click_landing_pad()
                    if rd.random_chance(probability=.3):
                        self.take_break(min_seconds=2, max_seconds=4, fancy=True)

                    # after clicking on the cave wait to find the crab for a bit
                    # this prevents clicking on the cave repeatedly while crab is waiting to spawn.
                    for _ in range(10):
                        if not self.find_crab():
                            time.sleep(1)
                        else:
                            break

            percent = (time.time() - start_time) / (self.running_time * 60) * 100
            self.log_msg(f"{percent:.2f}% done")

        self.end_script("Finished")
    
    def end_script(self, msg):
        self.update_progress(1)
        self.log_msg(msg)
        self.logout()
        self.stop()
        return 

    def click_crab(self):
        res = self.find_click_tag(self.crab_color, "Attack", clr.OFF_WHITE)
        if not res:
            self.errors += 1
            self.log_msg("could not find click crab")
        else:
            self.cave_consec = 0
        self.take_break(min_seconds=1, max_seconds=2, fancy=True)
        return res

    def click_landing_pad(self):
        res = self.find_click_tag(self.landing_pad_color, "Walk here", clr.OFF_WHITE)
        if not res:
            self.errors += 1
            self.log_msg("could not find click landing pad")
        return res

    def click_cave(self):
        res = self.find_click_tag(self.cave_color, "Crawl-through", clr.OFF_WHITE)
        if not res:
            self.errors += 1
            self.log_msg("could not find click cave")
        self.take_break(min_seconds=2, max_seconds=3, fancy=True)
        self.cave_consec += 1
        return res

    def find_crab(self):
        tag = self.loop_find_tag(self.crab_color)
        if not tag:
            return False
        return True

    def wait_for_kill(self):
        # small chance to click crab. 
        base_cycles_inverse = (10.0*60.0 / 15.0)**-1.0
        reclick_chance = .20 * base_cycles_inverse

        prev_xp = self.get_total_xp()
        errors = 0 
        while self.find_crab():
            self.take_break(min_seconds=1, max_seconds=45, fancy=True)

            if prev_xp == self.get_total_xp() or self.get_total_xp() == -1:
                errors += 1
                self.click_crab()
            else:
                errors = 0
            if errors > 3:
                self.end_script("Errored out, was not gaining xp when we thought we were")
            
            # click crab
            if rd.random_chance(probability=reclick_chance):
                self.click_crab()
            # move mouse randomly 
            if rd.random_chance(probability=reclick_chance):
                self.mouse.move_to(self.win.rectangle().random_point())
                time.sleep(1)
            
        return 