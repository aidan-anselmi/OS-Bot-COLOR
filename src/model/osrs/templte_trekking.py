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
from pynput.keyboard import Key, Controller
import utilities.ocr as ocr
import math
from pathlib import Path

class TemplteTrekker(OSRSBot):
    def __init__(self):
        bot_title = "Woodcutter"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 60

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)

        self.keyboard = Controller()

    def create_options(self):
        return
    
    def scrape(self):
        scraper = SpriteScraper()

        # set destination directory to src/images/bot/items (project-relative)
        dest_dir = Path(__file__).resolve().parents[2].joinpath("images", "bot", "items")
        # make sure directory exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        search_string = "Short vine, Long vine, Bowstring, Reward token, Logs"
        # search_string = "Deposit Inventory"
        image_type = ImageType.NORMAL
        destination = dest_dir

        self.path = scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)
        return 
    

    def save_options(self, options: dict):
        self.options_set = True
        return 
    
    def main_loop(self):
        start_time = time.time()
        end_time = self.running_time * 60
        errors = 0
        self.scrape()

        self.escort_color = clr.CYAN
        self.run_color = clr.PINK
        self.restart_color = clr.BLUE
        self.signpost_color = clr.Color([255, 144, 255])
        self.start_color = clr.WHITE
        self.vine_color = clr.YELLOW
        self.tree_color = clr.RED
        self.tree_sign = clr.ORANGE

        while time.time() - start_time < end_time and errors < 10:
            # escort 
            
            if self.loop_find_tag(self.vine_color, loops=1):
                #self.swing_vine()
                if self.loop_find_tag(clr.MINT, loops=3):
                    self.log_msg("swing vine saw tags!")
                    self.swing_vine()
                else:
                    self.click_legs()
            elif self.loop_find_tag(self.tree_sign, loops=1) and self.loop_find_tag(self.tree_color, loops=2):
                self.bridge_repair()
            elif self.loop_find_tag(self.restart_color, loops=1):
                self.log_msg("Restarting")
                self.click_legs()

            elif self.loop_find_tag(self.run_color, loops=1):
                self.handle_encounter()
            elif ocr.find_text(text="Route One", rect=self.win.game_view, font=ocr.QUILL_8, color=clr.Color([52, 52, 18])):
                time.sleep(1)
            
            elif self.loop_find_tag(self.escort_color, loops=1) and self.loop_find_tag(self.start_color, loops=1):
                # TODO open loot

                if not self.start_trek():
                    self.log_msg("could not start trek")
            self.update_progress((time.time() - start_time) / end_time)
            
            # elif route_rect := ocr.find_text(text="Route One", rect=self.win.game_view, font=ocr.QUILL_8, color=clr.Color([52, 52, 18])):
            #     self.find_click_rectangle(route_rect, mouseover_text="Select", color=clr.OFF_WHITE)

        self.click_legs()
        return
    
    def bridge_repair(self):
        pag.press(keys="f2")
        time.sleep(.1)
        if self.loop_find_tag(color=clr.MINT, loops=1):
            rect = self.loop_find_tag(color=clr.MINT, loops=1)
            if rect and rect.get_center()[0] < self.win.game_view.get_center()[0]:
                self.find_click_tag(clr.PINK, mouseover_text="Continue", color=clr.OFF_WHITE)
                time.sleep(1)
                self.sleep_until_not_moving(clr.MINT)
                time.sleep(1)

        for _ in range(3):
            self.find_click_tag(self.tree_color, mouseover_text="Chop", color=clr.OFF_WHITE)
            time.sleep(1)
            self.sleep_until_not_moving(clr.BLUE)
            time.sleep(1)
        
        if self.loop_find_image(image=self.path.joinpath("Logs.png"), rect=self.win.inventory, loops=3):
            for _ in range(3):
                log_rect = self.loop_find_image(image=self.path.joinpath("Logs.png"), rect=self.win.inventory, loops=3)
                if not log_rect:
                    break
                self.find_click_rectangle(log_rect, mouseover_text="Use", color=clr.OFF_WHITE)
                self.find_click_tag(clr.BLUE, mouseover_text="Use", color=clr.OFF_WHITE)
                time.sleep(1)
                self.sleep_until_not_moving(clr.BLUE)
                time.sleep(3.5)

        if self.loop_find_tag(color=clr.MINT, loops=3):
            self.find_click_tag(clr.MINT, mouseover_text="Cross", color=clr.OFF_WHITE)
            time.sleep(1)
            self.sleep_until_not_moving(clr.MINT)
            time.sleep(3)
            self.find_click_tag(clr.PINK, mouseover_text="Continue", color=clr.OFF_WHITE)
            time.sleep(1)
            self.sleep_until_not_moving(clr.MINT)
            time.sleep(1)

        
        return
    
    def swing_vine(self):
        pag.press(keys="f2")
        time.sleep(.1)
        red_rect = self.loop_find_tag(color=clr.RED, loops=3) 
        if red_rect and red_rect.get_center()[1] > self.win.game_view.get_center()[1]:
            self.find_click_tag(clr.PINK, mouseover_text="Continue", color=clr.OFF_WHITE)
            self.sleep_until_not_moving()
            return True

        if self.loop_find_image(image=self.path.joinpath("Long_vine.png"), rect=self.win.inventory, loops=1):
            self.find_click_image(image=self.path.joinpath("Long_vine.png"), rect=self.win.inventory, mouseover_text="Use", color=clr.OFF_WHITE)
            self.find_click_tag(clr.RED, mouseover_text="Use", color=clr.OFF_WHITE)
            time.sleep(1)
            self.sleep_until_not_moving()
            time.sleep(2)
            return True
        elif red_rect and self.find_click_rectangle(red_rect, mouseover_text="Swing", color=clr.OFF_WHITE):
            self.wait_till_interface_text("Great", font=ocr.QUILL_8, color=clr.BLACK)
            return True
        

        if self.loop_find_image(image=self.path.joinpath("Short_vine.png"), rect=self.win.inventory, loops=3):
            i = 0
            vine1 = None
            vine2 = None
            for i in range(28):
                if vine1 and vine2:
                    break
                if not vine1:
                    vine1 = self.loop_find_image(image=self.path.joinpath("Short_vine.png"), rect=self.win.inventory_slots[i], loops=1)
                elif not vine2:
                    vine2 = self.loop_find_image(image=self.path.joinpath("Short_vine.png"), rect=self.win.inventory_slots[i], loops=1)
            if vine1 and vine2:
                self.find_click_rectangle(vine1, mouseover_text="Use", color=clr.OFF_WHITE)
                self.find_click_rectangle(vine2, mouseover_text="Use", color=clr.OFF_WHITE)
                self.wait_till_interface_text("You twist", font=ocr.QUILL_8, color=clr.BLACK)

        for _ in range(3):
            self.find_click_tag(clr.MINT, mouseover_text="Cut", color=clr.OFF_WHITE)
            time.sleep(1)
            self.sleep_until_not_moving(clr.MINT)
            time.sleep(1)
        # cut vine
        # use vine on 
        return False
    
    def start_trek(self) -> bool:
        pag.press(keys="space")
        if not self.find_click_tag_with_missclick(self.escort_color, "Escort", clr.OFF_WHITE):
            if not self.find_click_tag_with_missclick(self.escort_color, "Escort", clr.OFF_WHITE):
                if not self.find_click_tag_with_missclick(self.escort_color, "Escort", clr.OFF_WHITE):
                    return False
        if not self.wait_till_interface_text("I can take", font=ocr.QUILL_8, color=clr.BLACK, max_wait=6):
            return False
        pag.press(keys="space")
        if not self.wait_till_interface_text("Oh really?", font=ocr.QUILL_8, color=clr.BLACK, max_wait=6):
            return False
        pag.press(keys="space")
        if not self.wait_till_interface_text("Okay", font=ocr.QUILL_8, color=clr.BLACK, max_wait=6):
            return False
        pag.press(keys="space")

        for _ in range(5):
            route_rect = ocr.find_text(text="Route One", rect=self.win.game_view, font=ocr.QUILL_8, color=clr.Color([52, 52, 18]))
            if route_rect:
                break
            time.sleep(1)
        if not route_rect:
            return False
        route_rect = route_rect[0]
        if not self.find_click_rectangle(route_rect, mouseover_text="Select", color=clr.OFF_WHITE):
            return False
        return True
    
    def handle_encounter(self) -> bool:
        for _ in range(5):
            if self.find_click_tag_with_missclick(self.run_color, "Evade", color=clr.OFF_WHITE):
                time.sleep(3)
                # wait until we dont see run color or it hs stopped moving
                self.sleep_until_not_moving()

                return True
            elif self.mouseover_text(contains="Continue", color=clr.OFF_WHITE):
                self.mouse.click()
                time.sleep(3)
                # wait until we dont see run color or it hs stopped moving
                self.sleep_until_not_moving()

                return True

            else:
                time.sleep(1)
        return False
    
    def sleep_until_not_moving(self, color=clr.PINK):
        while self.loop_find_tag(color, loops=3):
            prev = self.loop_find_tag(color, loops=1)
            time.sleep(.2)
            curr = self.loop_find_tag(color, loops=1)
            if prev and curr and math.dist(prev.get_center(), curr.get_center()) < 2:
                break
        return
    
    def open_loot(self):
        # find images in slots and open
        # click bowstrings
        # click claim
        # continue until all open 
        return
    
    def click_legs(self):
        if not self.find_click_rectangle(rectangle=self.win.inventory_slots[0], mouseover_text="Burgh", color=clr.OFF_WHITE):
            pag.press(keys="f2")
            time.sleep(.1)
            if not self.find_click_rectangle(rectangle=self.win.inventory_slots[0], mouseover_text="Burgh", color=clr.OFF_WHITE):
                return False
        time.sleep(3)
        return True