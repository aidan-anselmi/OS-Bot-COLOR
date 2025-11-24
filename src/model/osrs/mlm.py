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

class MLM(OSRSBot):
    def __init__(self):
        bot_title = "Woodcutter"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
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
    
    def scrape(self):
        scraper = SpriteScraper()

        # set destination directory to src/images/bot/items (project-relative)
        dest_dir = Path(__file__).resolve().parents[2].joinpath("images", "bot", "items")
        # make sure directory exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        search_string = "Uncut sapphire, Uncut emerald, Uncut ruby, Uncut diamond, Pay-dirt"
        # search_string = "Deposit Inventory"
        image_type = ImageType.NORMAL
        destination = dest_dir

        self.path = scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)
        return 

    def main_loop(self):
        self.current_action_rect = self.win.current_action
        self.current_action_rect.top += 25
        self.current_action_rect.height += 20
    
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()
        self.scrape()

        self.desposit_all_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        self.close_bank_img = imsearch.BOT_IMAGES.joinpath("bank", "close_bank.png")

        self.inventory_pixel_map = {}
        for i in range(len(self.win.inventory_slots)):
            self.inventory_pixel_map[i] = pag.pixel(*self.win.inventory_slots[i].get_center())

        self.sack_color = clr.GREEN
        self.up_ladder_color = clr.YELLOW
        self.down_ladder_color = clr.BLUE
        self.rock_color = clr.PINK
        self.hopper_color = clr.RED
        self.bank_color = clr.CYAN

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        self.errors = 0

        while time.time() - start_time < end_time and self.errors < 10:
            # mine until we have "full pay dirt"
            self.mining_loop()

            # empty sack
            if not self.empty_sack():
                self.log_msg("Failed to empty sack.")
                self.update_progress(1)
                return

            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        return 
    
    def mining_loop(self):
        sack_size = 108
        while sack_size > 10 and self.errors < 10:
            self.mine_inventory()
            self.log_msg(f"Completed mining inventory, current sack size {sack_size}")

            self.find_click_tag(self.hopper_color, "Deposit", clr.OFF_WHITE)
            nonempty_inventory_slots = self.nonempty_inventory_slots()
            sack_size -= nonempty_inventory_slots
            if nonempty_inventory_slots > 0:
                self.log_msg("Sack not empty after depositing, sack size {sack_size}, emptying sack.".format(sack_size=sack_size))
                self.drop_all()
                self.errors += 1
                sack_size = 0
                
        return
    
    def mine_inventory(self) -> int:
        self.drop_gems()
        self.mine_rock()

        while not self.full_inventory() and self.errors < 10:
            if not self.is_player_doing_action("Mining"):
                time.sleep(.5)
                if not self.is_player_doing_action("Mining", rect=self.win.current_action):
                    self.drop_gems()
                    self.mine_rock()

            if rd.random_chance(probability=0.95):
                self.take_break(min_seconds=2, max_seconds=12)
            else:
                self.take_break(min_seconds=30, max_seconds=75, fancy=True)
        return self.nonempty_inventory_slots()
    
    def mine_rock(self):
        if not self.click_rock():
            time.sleep(2)
            if not self.click_rock():
                self.log_msg("Failed to start mining")
                self.errors += 1
            else:
                time.sleep(5)
        else:
            time.sleep(5)

    def click_rock(self):
        rocks = self.get_all_tagged_in_rect(self.win.game_view, self.rock_color)
        rocks.sort(key=lambda r: Rectangle.distance_from_center(r.rect))
        if not rocks:
            self.log_msg("No rocks found.")
            return False
        
        rock = self.biased_reverse_pick(rocks)

        if not self.find_click_rectangle_with_missclick(rock, "Mine", clr.OFF_WHITE):
            self.log_msg("Could not click selected rock")
            self.errors += 1
            return False
        time.sleep(3)
        return True
    
    def biased_reverse_pick(self, items: list[RuneLiteObject], limit=4) -> RuneLiteObject:
        # weights: first item gets biggest weight, last gets smallest
        list_size = min(len(items), limit)
        weights = [(list_size - i)**1.5 for i in range(list_size)]   # e.g. [1,2,3,4,...]
        weighted_items = list(zip(items[:list_size], weights))

        for item, weight in reversed(weighted_items):
            if random.random() < (weight / sum(w for _, w in weighted_items)):
                return item

        # fallback if nothing hits
        return items[0]
    
    def full_inventory(self) -> bool:
        self.drop_gems()

        non_empty_slots = self.nonempty_inventory_slots()
        if rd.random_chance(probability=0.25) and non_empty_slots >= 22:
            return True
        if rd.random_chance(probability=0.5) and non_empty_slots >= 24:
            return True
        if non_empty_slots >= 26:
            return True
        return False
    
    def nonempty_inventory_slots(self) -> int:
        non_empty_slots = 0
        for i in range(len(self.win.inventory_slots)):
            slot_color = pag.pixel(*self.win.inventory_slots[i].get_center())
            if slot_color != self.inventory_pixel_map[i]:
                non_empty_slots += 1
        return non_empty_slots
    
    def drop_gems(self):
        self.log_msg("Dropping gems...")
        pag.keyDown('shift')
        for item in ["Uncut_sapphire.png", "Uncut_emerald.png", "Uncut_ruby.png", "Uncut_diamond.png"]:
            gem_img = imsearch.BOT_IMAGES.joinpath("items", item)
            while self.loop_find_image(gem_img, loops=5, sleep=0.01):
                self.find_click_image(gem_img)
            
        pag.keyUp("shift")
        return 
    
    def empty_sack(self) -> bool:
        self.log_msg("Emptying sack...")

        self.log_msg("Climbing down ladder...")
        if not self.find_click_tag_with_error(self.down_ladder_color, "Climb", clr.OFF_WHITE, "Could not find down ladder."):
            return False
        self.take_break(min_seconds=2, max_seconds=4)

        self.log_msg("Searching sack...")
        if not self.find_click_tag_with_error(self.sack_color, "Search", clr.OFF_WHITE, "Could not find sack."):
            return False
        self.take_break(min_seconds=5, max_seconds=6)

        while self.loop_find_tag(self.sack_color) and self.errors < 10:
            self.log_msg("Depositing items...")
            if not self.deposit_all(self.bank_color):
                self.errors += 1
                return False
            self.log_msg("Searching sack...")
            if not self.find_click_tag_with_error(self.sack_color, "Search", clr.OFF_WHITE, "Could not find sack."):
                return False
            self.take_break(min_seconds=4, max_seconds=5)

        if self.nonempty_inventory_slots() != 0:
            self.log_msg("Depositing items...")
            if not self.deposit_all(self.bank_color):
                self.errors += 1
                return False
        self.log_msg("Climbing up ladder...")
        if not self.find_click_tag_with_error(self.up_ladder_color, "Climb", clr.OFF_WHITE, "Could not find up ladder."):
            return False
        self.take_break(min_seconds=6, max_seconds=7)
        return True

    def find_click_tag_with_error(self, color: clr.Color, mouseover_text: str, color_check: clr.Color, error_msg: str) -> bool:
        if not self.find_click_tag(color, mouseover_text, color_check):
            self.log_msg(error_msg)
            self.errors += 1
            return False
        return True