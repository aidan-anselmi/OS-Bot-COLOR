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

# start this script with auto retaliate on by the bank in the WC guild ent dungeon
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
        

        while time.time() - start_time < end_time and self.errors < 10 and self.cave_consec < 4:
            time.sleep(1)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.stop()

        self.pick_up_loot
        return 

    def bank(self):
        # click bank
        # make sure we have an axe
        # grab food 
        return 

    def bank_from_ent_grounds(self):
        # if can't find root, 
        # step over root
        # bank
        return

    def chop_logs(self):
        # click logs CLOSEST TO PLAYER (far away logs could be someone else)
        # if hp goes below 40:
            # heal
            # reclick log
        # wait until log is gone
        return

    def fight_ent(self):
        # click a highlighted ent 
        # if we are not in combat soon (get_hp), tp and logout 
        # if hp dips below 40 
        return

    def chat_reader(self):
        # if we see a message that does not match:
            # You eat the x
            # It heals some health
            # The ent carcass yields
            # You swing your axe at the Ent Trunk
            # A bird's nest falls out of the tree.
        # Log message, tp, logout
        return 

    def heal(self):
        # if health below 40:
        # eat food until almost full
        # if no food, initiate bank 
        return 