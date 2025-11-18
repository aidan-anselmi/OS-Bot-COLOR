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

class OSRSWoodcutter(OSRSBot):
    def __init__(self):
        bot_title = "Woodcutter"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 135

        self.break_length_multiplier = random.uniform(.25, 1)
        self.break_chance_multiplier = random.uniform(.25, 1)
        self.tree_color = clr.PINK

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()
        self.logs = 0

        self.desposit_all_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        self.close_bank_img = imsearch.BOT_IMAGES.joinpath("bank", "close_bank.png")
        self.full_yew_logs = imsearch.BOT_IMAGES.joinpath("items", "full_yew_logs.png")

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            
            # deposit logs 
            if self.__full_inventory() or rd.random_chance(probability=0.1 * self.break_chance_multiplier):
                if not self.__deposit_logs():
                    continue 

            # chop tree 
            self.__chop_tree(next_nearest=False)

            # chance to move mouse or move to new tree while chopping 
            while not self.__full_inventory() and not api_m.get_is_player_idle():
                
                # chance to move trees 
                # yew trees last 114 seconds 
                if rd.random_chance(probabilit=1.0/(114.0 * 4.0)):
                    self.__chop_tree(next_nearest=True)

                # move mouse randomly 
                mouse_move_probability = 1.0/(150.0)
                if rd.random_chance(probabilit=mouse_move_probability):
                    self.move_mouse_off_screen()
                elif rd.random_chance(probabilit=mouse_move_probability):
                    self.move_mouse_random_point()
                time.sleep(1)

            # take a break 
            if rd.random_chance(probability=0.20 * self.break_chance_multiplier):
                self.take_break(max_seconds=90 * self.break_length_multiplier, fancy=True)

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
        tree = None
        if not trees:
            return False
        # If we are looking for the next nearest tree, we need to make sure trees has at least 2 elements
        if next_nearest and len(trees) < 2:
            return False
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

    def __chop_tree(self, next_nearest=False) -> bool:
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
        time.sleep(0.5)
        return True 

    def __full_inventory(self) -> bool:
        if imsearch.search_img_in_rect(self.full_yew_logs, self.win.inventory_slots):
            return True 
        return False