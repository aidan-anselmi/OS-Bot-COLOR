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

        self.empty_slot_clr_27 = pag.pixel(*self.win.inventory_slots[-1].get_center())
        self.empty_slot_clr_26 = pag.pixel(*self.win.inventory_slots[-2].get_center())
        self.empty_slot_clr_25 = pag.pixel(*self.win.inventory_slots[-3].get_center())
        self.empty_slot_clr_24 = pag.pixel(*self.win.inventory_slots[-4].get_center())

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
            else:
                if not self.__chop_tree():
                    errors += 1
                    continue 

            # chance to move mouse or move to new tree while chopping 
            while self.is_player_doing_action("Woodcutting"):
                # chance to move trees 
                # yew trees last 114 seconds 
                if rd.random_chance(probability=1.0/(114.0 * 4.0)):
                    self.__chop_tree()

                # chance that we are attentive of the contents of our inventory and end early if looking full
                # proabbility is to mimic that we check once every 20s
                if rd.random_chance(probability=1.0/20.0) and self.full_inventory():
                    break

                # move mouse randomly 
                if rd.random_chance(probability=(1.0/45.0)):
                    self.mouse.move_to(self.win.rectangle().random_point())
                    time.sleep(1)
                
                time.sleep(1)

                

            # take a long break 
            if rd.random_chance(probability=0.25 * self.break_chance_multiplier):
                self.take_break(max_seconds=60 * self.break_length_multiplier, fancy=True)
            # short break
            else:
                self.take_break(max_seconds=5, fancy=True)

            self.update_progress((time.time() - start_time) / end_time)

        self.log_msg(f"Script ran with {errors} errors")
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def __deposit_logs(self) -> bool:
        
        if not self.find_click_tag(self.bank_color, "Deposit", color=clr.OFF_WHITE):
            self.log_msg("could not click on bank deposit box")
            return False
        self.wait_till_bank_deposit_open()

        if not self.find_click_image(self.desposit_all_img):
            self.log_msg("could not find deposit all button")
            return False

        # chance to just start chopping logs
        if rd.random_chance(probability=.85):
            return self.__chop_tree()

        # hit close button 
        if not self.find_click_image(self.close_bank_img):
            self.log_msg("could not close the bank")
            return False
        
        return self.__chop_tree()

    def __chop_tree(self) -> bool:
        for _ in range(5):
            trees = self.get_all_tagged_in_rect(self.win.game_view, self.tree_color)
            trees = sorted(trees, key=RuneLiteObject.distance_from_rect_center)
            if len(trees) == 0:
                continue
            tree = trees[0]
            if len(trees) >= 2 and rd.random_chance(probability=.25):
                tree = trees[1]
            if self.find_click_rectangle(tree, mouseover_text="Chop", color=clr.OFF_WHITE):
                time.sleep(5)
                return True
        self.log_msg("no trees found")
        return False

    # Your inventory is too full to hold any more yew logs
    def full_inventory(self) -> bool:
        if pag.pixel(*self.win.inventory_slots[-1].get_center()) != self.empty_slot_clr_27:
            return True
        elif rd.random_chance(probability=.9) and pag.pixel(*self.win.inventory_slots[-2].get_center()) != self.empty_slot_clr_26:
            return True
        elif rd.random_chance(probability=.8) and pag.pixel(*self.win.inventory_slots[-3].get_center()) != self.empty_slot_clr_25:
            return True
        elif rd.random_chance(probability=.7) and pag.pixel(*self.win.inventory_slots[-4].get_center()) != self.empty_slot_clr_24:
            return True
        return False
