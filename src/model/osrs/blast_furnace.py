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

        coal_ratio = {"Iron ore": 1, "Mithril ore": 2}

        item_to_smith = "Iron ore"
        num_bars_to_make = 1400
        bars_made = 0
        while bars_made < num_bars_to_make - 28:
            # load with coal 
            for _ in range(coal_ratio[item_to_smith]):
                self.get_item_from_bank("Coal")
                self.place_conveyor_belt_item()

            # load with ore 
            self.get_item_from_bank(item_to_smith)
            self.place_conveyor_belt_item()

            # click on tiles by dispenser
            self.find_click_tag(self.tiles_by_dispenser, "Walk", clr.OFF_WHITE)

            # click on dispenser
            self.find_click_tag(self.bar_dispenser_clr, "Dispenser", clr.OFF_WHITE)

            # bank, deposit bars
            self.open_bank()
            self.find_click_image(self.desposit_all_img)
            bars_made += 28

    def open_bank(self):
        self.find_click_tag(self.bank_clr, "Use", clr.OFF_WHITE)
        self.wait_till_bank_deposit_open()
        return

    def get_item_from_bank(self, item):
        self.open_bank()
        img = imsearch.BOT_IMAGES.joinpath("items", item + "_bank.png")
        self.find_click_image(img)
        pag.press('esc')
        return
    
    def place_conveyor_belt_item(self):
        self.find_click_rectangle_with_missclick(self.conveyor_belt_clr, "Deposit-ore-on", clr.OFF_WHITE)
        time.sleep(3)
        for i in range(100):
            if not self.full_inventory():
                return True
            # every 2 seconds try to reclick
            if i % 10 == 0:
                self.find_click_rectangle_with_missclick(self.conveyor_belt_clr, "Deposit-ore-on", clr.OFF_WHITE)
            time.sleep(0.2)
        return False
    
    def get_bars(self, object_color: clr.Color) -> bool:
        tag = self.loop_find_tag(object_color)
        if not tag:
            self.log_msg("could not find tag")
            return False

        self.mouse.move_to(tag.random_point())
        self.mouse.click()
        return True
    
    def full_inventory(self) -> bool:
        if pag.pixel(*self.win.inventory_slots[-1].get_center()) != self.empty_slot_clr_27:
            return True
        return False
    
