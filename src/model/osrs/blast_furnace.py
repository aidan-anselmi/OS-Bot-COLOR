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

class BlastFurnace(OSRSBot):
    def __init__(self):
        bot_title = "Blast Furnace"
        description = (
            """
            Checklist:
            - empty inventory
            - zoomed all the way out
            - facing north and slightly down

            """
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 180

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

        search_string = "Iron ore, Coal, Gold ore, Mithril ore, Adamantite ore, Runite ore"
        # search_string = "Deposit Inventory"
        image_type = ImageType.BANK
        destination = dest_dir

        self.path = scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)
        return 

    def main_loop(self):    
        self.scrape()
        self.log_msg("Selecting inventory...")
        pag.press('f2')

        self.desposit_all_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        self.empty_slot_clr_27 = pag.pixel(*self.win.inventory_slots[-1].get_center())

        
        self.inventory_pixel_map = {}
        for i in range(len(self.win.inventory_slots)):
            self.inventory_pixel_map[i] = pag.pixel(*self.win.inventory_slots[i].get_center())

        self.conveyor_belt_clr = clr.BLUE
        self.bar_dispenser_clr = clr.RED
        self.tiles_by_dispenser = clr.GREEN
        self.bank_clr = clr.PINK

        coal_ratio = {"Iron_ore": 1, "Mithril_ore": 2}

        item_to_smith = "Iron_ore"
        num_bars_to_make = 1400
        bars_made = 0
        self.errors = 0
        while bars_made < num_bars_to_make - 28 and self.errors < 10:
            # load with coal 
            for _ in range(coal_ratio[item_to_smith]):
                self.get_item_from_bank("Coal")
                self.place_conveyor_belt_item()

            # load with ore 
            self.get_item_from_bank(item_to_smith)
            self.place_conveyor_belt_item()

            # get bars
            self.get_bars()

            # bank, deposit bars
            self.open_bank()
            self.find_click_image(self.desposit_all_img)
            bars_made += 28

    def open_bank(self):
        self.find_click_tag(self.bank_clr, "Use", clr.OFF_WHITE)
        self.wait_till_bank_open()
        return

    def get_item_from_bank(self, item):
        if not self.is_bank_open():
            self.open_bank()
        
        img = imsearch.BOT_IMAGES.joinpath("items", item + "_bank.png")
        if not self.find_click_image(img):
            self.log_msg(f"Could not find {item} in bank")
            self.errors += 1
            return False
        self.take_break(min_seconds=.2, max_seconds=.7)
        pag.press('esc')
        return
    
    def place_conveyor_belt_item(self):
        self.find_click_tag(self.conveyor_belt_clr, "Put-ore-on", clr.OFF_WHITE)
        self.take_break(min_seconds=0.5, max_seconds=1.0)
        self.turn_on_run()
        self.wait_until_not_moving()
        for i in range(200):
            if not self.full_inventory():
                return True
            # every 2 seconds try to reclick
            if i % 20 == 0:
                self.find_click_tag(self.conveyor_belt_clr, "Put-ore-on", clr.OFF_WHITE)
            time.sleep(0.1)
        return False
    
    def get_bars(self) -> bool:
        if self.full_inventory():
            self.log_msg("Inventory full before getting bars")
            return True

        # click on tiles by dispenser
        if rd.random_chance(0.4):
            tag = self.loop_find_tag(self.tiles_by_dispenser)
        else:
            tag = self.loop_find_tag(self.bar_dispenser_clr)
        self.mouse.move_to(tag.random_point())
        self.mouse.click()
        self.take_break(min_seconds=0.8, max_seconds=2)

        # Thhe dispenser doesn't contain any bars.

        # How many would you likve to take? (bold)
        # Chooose a quantity

        with pag.hold('space'):
            self.wait_until_not_moving()
            time.sleep(.2)
            # inventyory open
            if self.get_all() or self.full_inventory():
                if self.wait_until_full_inventory():
                    return True
                else:
                    self.log_msg("Inventory did not fill after getting bars")
                    self.errors += 1
                    return self.get_bars()



            tag = self.loop_find_tag(self.bar_dispenser_clr)
            if not tag:
                self.log_msg("could not find tag")
                return False
        
            # Check
            # Take -> hit space
            self.mouse.move_to(tag.random_point())
            while self.mouseover_text(contains="Check", color=clr.OFF_WHITE):
                if rd.random_chance(0.3):
                    self.mouse.click()
                self.take_break(min_seconds=0.1, max_seconds=0.4)
            if not self.mouseover_text(contains="Take", color=clr.OFF_WHITE):
                self.errors += 1
                self.log_msg("Could not find Take option on dispenser")
                return self.get_bars()
            self.mouse.click()
            if self.wait_until_full_inventory():
                return True
            else:
                self.log_msg("Inventory not full after taking bars, retrying...")
                return self.get_bars()

    def wait_until_full_inventory(self, timeout: int = 20) -> bool:
        for _ in range(timeout * 10):
            if self.full_inventory():
                return True
            time.sleep(0.1)
        self.errors += 1
        self.log_msg("Inventory did not fill in time")
        return False
    
    def full_inventory(self) -> bool:
        if pag.pixel(*self.win.inventory_slots[-1].get_center()) != self.empty_slot_clr_27:
            return True
        return False
    
    def turn_on_run(self):
        if self.get_run_energy() == 100 and rd.random_chance(0.8):
            self.find_click_rectangle(self.win.run_orb, "Toggle Run", color=clr.OFF_WHITE)
            return True
        return False
    
    def wait_until_not_moving(self):
        # if the relative_tile is moving, we are actually moving

        relative_tile_color = self.tiles_by_dispenser
        # wait max of 10 seconds
        prev_center = self.loop_find_tag(relative_tile_color).get_center()
        time.sleep(0.1)
        for _ in range(200):
            cur_center = self.loop_find_tag(relative_tile_color).get_center()
            if math.dist(prev_center, cur_center) < 2:
                return True
            else:
                prev_center = cur_center
                time.sleep(0.1)

        self.errors += 1
        self.log_msg("Player did not stop moving in time")
        return False
