import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Point, RuneLiteObject, Rectangle
import random
import math
from utilities.sprite_scraper import SpriteScraper, ImageType
import utilities.imagesearch as imsearch
import pyautogui as pag
from pathlib import Path
import utilities.runelite_cv as rcv
import keyboard

class WyrmAgility(OSRSBot):
    def __init__(self):
        bot_title = "Wyrm Agility"
        description = (
            """
            Checklist:
            - empty inventory
            - zoomed all the way out
            - facing north and slightly down

            """
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 175

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)

    def create_options(self):
        return

    def save_options(self, options: dict):
        self.options_set = True
        return 

    def main_loop(self):        
        self.obstacle_color_1 = clr.GREEN

        start_time = time.time()
        end_time = self.running_time * 60
        self.errors = 0

        order = ["Climb", "Cross", "Climb", "Jump", "Cross", "Slide"]
        cur = self.loop_find_tag(clr.GREEN)
        self.mouse.move_to(cur.random_point())
        time.sleep(1)
        i = 0
        while i < len(order):
            if self.mouseover_text(contains=order[i], color=clr.OFF_WHITE):
                self.log_msg(f"Starting obstacle found: {order[i]}")
                break
            else:
                self.log_msg(f"'{self.mouseover_text()}' does not start with '{order[i]}'")
                self.mouse.move_to(cur.random_point())
                i += 1
                time.sleep(.1)

        time_since_last_click = time.time()
        while time.time() - start_time < end_time and self.errors < 5:
            if time.time() - time_since_last_click > 300:
                self.log_msg("No obstacles clicked for 5 minutes, ending bot.")
                return
            
            if self.find_click_tag_with_missclick(clr.GREEN, mouseover_text=order[i], color=clr.OFF_WHITE):
                time_since_last_click = time.time()
                i += 1
                if i >= len(order):
                    i = 0
                time.sleep(1)
                self.wait_until_not_moving()
            elif self.find_click_tag(clr.GREEN, mouseover_text=order[i-1], color=clr.OFF_WHITE):
                self.log_msg(f"Mouseover text '{self.mouseover_text()}' indicates previous obstacle not completed.")
                time.sleep(1)
                self.wait_until_not_moving()
                    

            if rd.random_chance(.02):
                self.take_break(min_seconds=30, max_seconds=200)
            elif rd.random_chance(.08):
                self.take_break(min_seconds=2, max_seconds=8)
            elif rd.random_chance(.1):
                self.take_break(min_seconds=.5, max_seconds=2)

    def wait_until_not_moving(self):
        # if the relative_tile is moving, we are actually moving

        # wait max of 30 seconds
        prev_center = Point(0,0)
        time.sleep(0.1)
        for _ in range(300):
            cur_tag = self.loop_find_tag(clr.GREEN)
            if not cur_tag:
                time.sleep(0.1)
                continue
            
            cur_center = cur_tag.get_center()
            if math.dist(prev_center, cur_center) < 2:
                return True
            else:
                prev_center = cur_center
                time.sleep(0.1)

        self.errors += 1
        self.log_msg("Player did not stop moving in time")
        return False


    # def get_starting_tag(self) -> clr.Color:
    #     closest_1_tag = self.loop_find_tag(self.obstacle_color_1)
    #     closest_2_tag = self.loop_find_tag(self.obstacle_color_2)
    #     cur_tag = None
    #     if closest_1_tag and closest_2_tag:
    #         closest_1_tag.distance_from_rect_center()
    #         closest_2_tag.distance_from_rect_center()
    #         if closest_1_tag.distance_from_rect_center() < closest_2_tag.distance_from_rect_center():
    #             cur_tag = self.obstacle_color_1
    #         else:
    #             cur_tag = self.obstacle_color_2
    #     elif closest_1_tag:
    #         cur_tag = self.obstacle_color_1
    #     elif closest_2_tag:
    #         cur_tag = self.obstacle_color_2
    #     return cur_tag
    
    # def iterate_tag(self, cur_tag: clr.Color) -> clr.Color:
    #     if cur_tag == self.obstacle_color_1:
    #         return self.obstacle_color_2
    #     return self.obstacle_color_1
    
    # def is_moving(self, tracking_color: clr.Color) -> bool:
    #     if not self.color_tracker:
    #         self.color_tracker = {}
    #     if not self.color_tracker.get(tracking_color):
    #         self.color_tracker[tracking_color] = self.loop_find_tag(tracking_color)
    #         return True
        
    #     center = self.loop_find_tag(tracking_color).get_center()
    #     if not center:
    #         return True
    #     return math.dist(center, self.color_tracker[tracking_color].get_center()) > 2
    
    # def is_closer_color(self, tracking_color: clr.Color) -> bool:
    #     tracking_tag = self.loop_find_tag(tracking_color)
    #     other_tag = self.loop_find_tag(self.iterate_tag(tracking_color))
    #     if not tracking_tag and not other_tag:
    #         return False
    #     if not tracking_tag:
    #         return False
    #     if not other_tag:
    #         return True
    #     return tracking_tag.distance_from_rect_center() < other_tag.distance_from_rect_center()
    
    # def wait_until_not_moving_and_closer(self, tracking_color: clr.Color):
    #     for _ in range(300):
    #         if not self.is_moving(tracking_color) and self.is_closer_color(tracking_color):
    #             return True
    #         time.sleep(0.1)
    #     return False