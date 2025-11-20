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

class OSRSWoodcutter(OSRSBot):
    def __init__(self):
        bot_title = "Woodcutter"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120

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
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        self.desposit_all_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        self.close_bank_img = imsearch.BOT_IMAGES.joinpath("bank", "close_bank.png")

        x, y = self.win.inventory_slots[-1].get_center()
        self.empty_slot_clr = pag.pixel(x, y)

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        errors = 0
        while time.time() - start_time < end_time and errors < 10:
            
            # deposit logs 
            if self.full_inventory() or rd.random_chance(probability=0.025 * self.break_chance_multiplier):
                if not self.__deposit_logs():
                    errors += 1
                    continue 

            # chop tree 
            self.__chop_tree()

            # chance to move mouse or move to new tree while chopping 
            while not self.full_inventory() and self.is_player_doing_action("Woodcutting"):
                # chance to move trees 
                # yew trees last 114 seconds 
                if rd.random_chance(probability=1.0/(114.0 * 8.0)):
                    self.__chop_tree()

                # move mouse randomly 
                if rd.random_chance(probability=(1.0/45.0)):
                    self.mouse.move_to(self.win.rectangle().random_point())
                else:
                    time.sleep(1)

            # take a long break 
            if rd.random_chance(probability=0.25 * self.break_chance_multiplier):
                self.take_break(max_seconds=60 * self.break_length_multiplier, fancy=True)
            # short break
            else:
                self.take_break(max_seconds=5, fancy=True)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def __move_mouse_to_nearest_tree(self, next_nearest=False):
        """
        Locates the nearest tree and moves the mouse to it. This code is used multiple times in this script,
        so it's been abstracted into a function.
        Args:
            next_nearest: If True, will move the mouse to the second nearest tree. If False, will move the mouse to the
                          nearest tree.
            mouseSpeed: The speed at which the mouse will move to the tree. See mouse.py for options.
        Returns:
            True if success, False otherwise.
        """
        trees = self.get_all_tagged_in_rect(self.win.game_view, self.tree_color)
        if not trees:
            return False
        # If we are looking for the next nearest tree, we need to make sure trees has at least 2 elements
        if next_nearest and len(trees) < 2:
            next_nearest = False
        trees = sorted(trees, key=RuneLiteObject.distance_from_rect_center)
        tree = trees[1] if next_nearest else trees[0]
        if next_nearest:
            self.mouse.move_to(tree.random_point(), mouseSpeed="slow", knotsCount=2)
        else:
            self.mouse.move_to(tree.random_point())
        return True

    def __deposit_logs(self) -> bool:
        
        if not self.find_click_tag(self.bank_color, "Deposit", color=clr.OFF_WHITE):
            self.log_msg("could not click on bank deposit box")
            return False
        self.wait_till_bank_deposit_open()

        if not self.find_click_image(self.desposit_all_img):
            self.log_msg("could not find deposit all button")
            return False

        # chance to just start chopping logs

        # hit close button 
        if not self.find_click_image(self.close_bank_img):
            self.log_msg("could not close the bank")
            return False
        
        return 

    def __chop_tree(self) -> bool:
        next_nearest =  rd.random_chance(probability=.25)

        failed_searches = 0
        # If our mouse isn't hovering over a tree, and we can't find another tree...
        if not self.mouseover_text(contains="Chop", color=clr.OFF_WHITE) and not self.__move_mouse_to_nearest_tree(next_nearest):
            failed_searches += 1
            if failed_searches % 10 == 0:
                self.log_msg("Searching for trees...")
            if failed_searches > 60:
                # If we've been searching for a whole minute...
                self.__logout("No tagged trees found. Logging out.")
            time.sleep(1)
            return False
        failed_searches = 0  # If code got here, a tree was found

        # Click if the mouseover text assures us we're clicking a tree
        if not self.mouseover_text(contains="Chop", color=clr.OFF_WHITE):
            return False
        self.mouse.click()
        time.sleep(5) # sleep a bit to wait for action to update
        return True 

    # Your inventory is too full to hold any more yew logs
    def full_inventory(self) -> bool:
        x, y = self.win.inventory_slots[-1].get_center()
        return pag.pixel(x, y) != self.empty_slot_clr