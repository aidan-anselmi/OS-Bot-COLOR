import time

import numpy as np

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
import utilities.ocr as ocr
import cv2

exclude_chars = [
    "Ì",
    "Í",
    "Î",
    "Ï",
    "ì",
    "í",
    "î",
    "ï",
    "Ĺ",
    "Ļ",
    "Ľ",
    "Ŀ",
    "Ł",
    "ĺ",
    "ļ",
    "ľ",
    "ŀ",
    "ł",
    "|",
    "¦",
    "!",
    "ĵ",
    "ǰ",
    "ȷ",
    "ɉ",
    "Ĵ",
    "Ĩ",
    "Ī",
    "Ĭ",
    "Į",
    "İ",
    "Ɨ",
    "Ỉ",
    "Ị",
    "ĩ",
    "ī",
    "ĭ",
    "į",
    "ı",
    "ƚ",
    "ỉ",
    "ị",
    "ˈ",
    "ˌ",
    "ʻ",
    "ʼ",
    "ʽ",
    "˚",
    "˙",
    "ʾ",
    "ʿ",
    ",",
    "˙",
    "`",
    "(",
    ")",
    "%",
]
# Also exclude all ASCII alphabetic characters (lower and upper) by default
alphabet_lower = [chr(c) for c in range(ord('a'), ord('z') + 1)]
alphabet_upper = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
exclude_chars.extend(alphabet_lower + alphabet_upper)
green = clr.Color([55, 240, 70])
red = clr.Color([230, 30, 30])
orange = clr.Color([230, 150, 30])
grey = clr.Color([165, 165, 165])
colors = [green, red, orange, grey]

class GiantsFoundry(OSRSBot):
    def __init__(self):
        bot_title = "Giants Foundry"
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
        self.tag_map = {}

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

        search_string = "Mithril bar, Steel bar"
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
        self.log_msg("Selecting inventory...")
        #pag.press('f2')
        self.scrape()

        self.bank_color = clr.PINK
        self.active_station_color = clr.GREEN
        self.warning_station_color = clr.ORANGE
        self.bonus_color = clr.PURPLE
        self.mould_text_color = clr.BLUE
        self.general_color = clr.BLUE
        self.lava_color = clr.WHITE
        self.waterfall_color = clr.YELLOW        

        self.status_window = Rectangle(
            left=10 + self.win.game_view.left,
            top=25 + self.win.game_view.top,
            width=145,
            height=80,
        )
        
        self.heat_window = Rectangle(
            left=10 + self.win.game_view.left + 100,
            top=25 + self.win.game_view.top,
            width=45,
            height=20,
        )
        self.current_stage_window = Rectangle(
            left=10 + self.win.game_view.left + 45,
            top= self.heat_window.top + self.heat_window.height - 2,
            width=100,
            height=18,
        )
        self.actions_left_window = Rectangle(
            left=10 + self.win.game_view.left + 100,
            top= self.current_stage_window.top + self.current_stage_window.height - 2,
            width=45,
            height=18,
        )
        self.heat_left_window = Rectangle(
            left=10 + self.win.game_view.left + 100,
            top= self.actions_left_window.top + self.actions_left_window.height - 2,
            width=45,
            height=18,
        )

    
        start_time = time.time()
        end_time = self.running_time * 60
        self.errors = 0
        while time.time() - start_time < end_time and self.errors < 10:
            if not self.loop_find_tag(self.active_station_color, loops=3):
                if not self.setup_sword():
                    self.log_msg("Failed to setup sword, retrying")
                    self.errors += 1
                    continue
            self.make_sword()
            self.hand_in_sword()

            if rd.random_chance(0.15):
                self.take_break(min_seconds=10, max_seconds=20)
            elif rd.random_chance(0.05):
                self.take_break(min_seconds=30, max_seconds=90)

    def setup_sword(self) -> bool:
        #self.get_commission()
        self.take_break(min_seconds=0, max_seconds=.5)
        if not self.set_mould():
            self.log_msg("Failed to set mould")
            return False
        self.get_bars()
        self.add_bars_to_crucible()
        self.find_click_tag(self.active_station_color, "Pour", color=clr.OFF_WHITE)
        self.take_break(min_seconds=1, max_seconds=3)
        self.find_click_tag(self.general_color, "Pick-up", color=clr.OFF_WHITE)
        self.take_break(min_seconds=5.5, max_seconds=8)
        return True

    def get_commission(self):
        kovac = self.loop_find_tag(clr.CYAN)
        if not kovac:
            self.log_msg("Could not find Kovac to get commission")
            return False
        self.mouse.move_to(kovac.random_point())
        self.mouse.right_click()
        if take_text := ocr.find_text(
                "Commission",
                self.win.game_view,
                ocr.BOLD_12,
                clr.WHITE,
            ):
            self.mouse.move_to(take_text[0].random_point(), mouseSpeed="medium")
            self.mouse.click()
            time.sleep(3)
            return True
        self.log_msg("Could not find commission option when right clicking Kovac")
        return False

    def set_mould(self):
        # TODO shrink search area to just the mould interface
        # TODO expand text selection out to get larger rectangle

        if not self.find_click_tag(self.general_color, "Setup", color=clr.OFF_WHITE):
            self.log_msg("Failed to find and click setup station")
            return False
        time.sleep(4)

        blade_parts = ["Forte", "Blades", "Tips"]
        if rd.random_chance(0.4):
            blade_parts.reverse()

        tab_selects = 0
        for blade_part in blade_parts:
            tab_rects = ocr.find_text(blade_part, self.win.game_view, ocr.PLAIN_12, clr.OFF_ORANGE)
            if not tab_rects:
                tab_rects = ocr.find_text(blade_part, self.win.game_view, ocr.PLAIN_12, clr.OFF_ORANGE)
            if not tab_rects:
                self.log_msg(f"Could not find {blade_part} tab when setting mould")
                return False
            if len(tab_rects) != 1:
                self.log_msg(f"Expected 1 text rect when selecting tab, found {len(tab_rects)}")
                return False
            if self.find_click_rectangle(tab_rects[0], "View", color=clr.OFF_WHITE):
                tab_selects += 1

            search_texts = ["Needle Point", "Defenders Tip", "Serrated Tip", "Saw Tip", "Gladius Point", "Serpent's Fang", "Medusa's Head", "Chopper Tip", "People Poker Point"]
            if blade_part == "Forte":
                search_texts = ["Defender Base", "Stiletto Forte", "Chopper Forte +1", "Juggernaut Forte", "Serrated Forte", "Serpent Ricasso", "Medusa Ricasso", "Disarming Forte", "Gladius Ricasso", "Chopper Forte"]
            elif blade_part == "Blades":
                search_texts = ["Serpent Blade", "Fleur de Blade", "Claymore Blade", "Flamberge Blade", "Gladius Edge", "Stiletto Blade", "Medusa Blade", "Fish Blade", "Defenders Edge", "Saw Blade"]
            mould_rects = ocr.find_text(search_texts, self.win.game_view, ocr.BOLD_12, self.mould_text_color)
            if not mould_rects:
                mould_rects = ocr.find_text(search_texts, self.win.game_view, ocr.BOLD_12, self.mould_text_color)
            if not mould_rects:
                self.log_msg("No text found when setting mould")
                return False
            if len(mould_rects) != 1:
                self.log_msg(f"Expected 1 text rect when setting mould, found {len(mould_rects)}")
                return False
            if not self.find_click_rectangle(mould_rects[0], "Select", color=clr.OFF_WHITE):
                self.log_msg("Failed to click mould when setting mould")
                return False

        if tab_selects < 2:
            self.log_msg(f"Expected to click 2 tab selects when setting mould, clicked {tab_selects}")
        pag.press('esc')
        return True
    
    def select_tab(self, tab_name: str):
        tab_name = tab_name.lower()
        path = imsearch.BOT_IMAGES.joinpath("giants_foundry", f"{tab_name}_large_selected.png")
        self.log_msg(f"Selecting tab {path}")
        # make sure it exists
        if not path.exists():
            self.log_msg(f"Tab image does not exist: {path}")
            return False

        if self.loop_find_image(path, self.win.game_view, loops=3):
            return True
        path = imsearch.BOT_IMAGES.joinpath("giants_foundry", f"{tab_name}_large_tab.png")
        if not path.exists():
            self.log_msg(f"Tab image does not exist: {path}")
            return False
        if self.find_click_image(path, self.win.game_view, "View"):
            return True
        return False
    
    def get_bars(self):
        self.find_click_tag(self.bank_color, "Use", color=clr.OFF_WHITE)
        self.wait_till_bank_open()
        self.find_click_image(self.path.joinpath("Mithril_bar_bank.png"))
        self.take_break(min_seconds=0.1, max_seconds=0.5)
        self.find_click_image(self.path.joinpath("Steel_bar_bank.png"))
        self.take_break(min_seconds=1, max_seconds=2)
        pag.press('esc')
        return
    
    def add_bars_to_crucible(self):
        order = ["3", "4"]
        if rd.random_chance(0.2):
            order.reverse()

        for button in order:
            self.find_click_tag(self.general_color, "Fill", color=clr.OFF_WHITE)
            self.wait_till_interface_text("What metal")
            self.take_break(min_seconds=.5, max_seconds=1.5)
            pag.press(button)
            if not self.wait_till_interface_text("You add", ocr.QUILL_8, clr.BLACK):
                self.log_msg("Failed to confirm bars added to crucible")
        return
    
    def hand_in_sword(self):
        self.log_msg("Handing in sword...")
        self.find_click_tag(clr.CYAN, "Hand-in", color=clr.OFF_WHITE)
        if not self.wait_till_interface_text("Hmm", ocr.QUILL_8, clr.BLACK):
            self.log_msg("Failed to find hand-in interface")
            return
        self.take_break(min_seconds=.5, max_seconds=1)
        pag.press('space')
        if not self.wait_till_interface_text("Smithing", ocr.QUILL_8, clr.BLACK):
            self.log_msg("Failed to confirm sword handed in")
            return
        self.take_break(min_seconds=1, max_seconds=3)
        pag.press('space')
        if not self.wait_till_interface_text("Yes", ocr.QUILL_8, clr.BLACK):
            self.log_msg("Failed to confirm receive another commission")
            return
        self.take_break(min_seconds=1, max_seconds=2)
        pag.press('1')
        self.take_break(min_seconds=1, max_seconds=3)
        # confirm we got the comission
        return
    
    def has_tag_moved(self, tag: clr.Color) -> bool:
        initial_tag = self.loop_find_tag(tag)
        if not initial_tag:
            return True
        
        if not tag in self.tag_map:
            self.tag_map[tag] = initial_tag.get_center()
            return True
        if math.dist(self.tag_map[tag], initial_tag.get_center()) > 5:
            self.tag_map[tag] = initial_tag.get_center()
            return True
        return False
    
    def wait_until_tag_moves(self, tag: clr.Color, timeout: int = 30) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.has_tag_moved(tag):
                return True
            time.sleep(0.1)
        self.log_msg(f"Tag {tag} did not move within timeout")
        self.errors += 1
        return False
    
    def wait_until_tag_stops_moving(self, tag: clr.Color, timeout: int = 30) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.has_tag_moved(tag):
                return True
            time.sleep(0.1)
        self.log_msg(f"Tag {tag} did not stop moving within timeout")
        self.errors += 1
        return False
    
    def fix_heat(self, first_try: bool = True):
        # get heat
        # get tarted heat
        # heat or cool until done
        # click on self tile 
        # TODO temp incrrease accelerates, account for this 

        heat_left = self.get_heat_left()
        if heat_left >= 2:
            return first_try

        current_heat = self.get_current_heat()
        current_stage = self.get_current_stage()
        if current_heat == -1 or heat_left == -1 or current_stage == "unknown":
            return False
        
        target_min, target_max = self.get_target_heat_range(current_stage)
        if target_min == -1:
            return False
        if current_stage == "Hammer":
            target_min += 3
        elif current_stage == "Grind":
            target_max -= 3
        elif current_stage == "Polish":
            target_min += 3
        
        # if current_heat >= target_min and current_heat <= target_max:
        #     return first_try

        heating = False
        if current_heat <= target_min:
            heating = True
            if not self.find_click_tag(self.lava_color, "Heat", color=clr.OFF_WHITE):
                self.log_msg("Failed to click lava to heat, retrying")
                return self.fix_heat(False)
            time.sleep(2)
            self.wait_until_tag_stops_moving(self.lava_color)
        elif current_heat >= target_max:
            if not self.find_click_tag(self.waterfall_color, "Cool", color=clr.OFF_WHITE):
                self.log_msg("Failed to click waterfall to cool, retrying")
                return self.fix_heat(False)
            time.sleep(2)
            self.wait_until_tag_stops_moving(self.waterfall_color)
        time.sleep(1.5)
            
        target_heat = 7
        if current_stage == "Hammer":
            target_heat = 7
        elif current_stage == "Grind":
            target_heat = 12
        elif current_stage == "Polish":
            target_heat = 11
        # if current_stage == "Hammer":
        #     target_min = target_max - 5
        # elif current_stage == "Grind":
        #     target_max = target_min + 5
        # elif current_stage == "Polish":
        #     target_min = target_max - 5        

        actions_left = self.get_actions_left()
        start_time = time.time()
        while True:
            loop_current_heat = self.get_current_heat()
            heat_left = self.get_heat_left()
            if heating and loop_current_heat <= current_heat:
                self.log_msg(f"Heating but heat did not increase, retrying")
                return self.fix_heat(False)
            elif not heating and time.time() - start_time > 8 and loop_current_heat >= current_heat - 3:
                self.log_msg(f"Cooling but heat did not decrease, retrying")
                return self.fix_heat(False)

            if heat_left >= target_heat  or (heat_left - actions_left >= 2):
                self.log_msg(f"Corrected heat withe heat left: {heat_left}, actions left: {actions_left}")
                self.click_self_tile()                        
                return self.fix_heat(False)
            elif heating and loop_current_heat >= target_max:
                return self.fix_heat(False)
            elif not heating and loop_current_heat <= target_min:
                return self.fix_heat(False)
            
    
    def get_heat_left(self) -> int:
        # red orange or green
        for _ in range(3):
            heat = self.get_heat_left_helper()
            if heat != -1:
                return heat
            time.sleep(0.1)
        return -1 
    
    def get_heat_left_helper(self) -> int:
        # img_rect = self.heat_left_window.screenshot()
        # cv2.imwrite(f"heat_left_window.png", np.array(img_rect))
        heat = ocr.extract_text(self.heat_left_window, ocr.PLAIN_12, [red, orange, green], exclude_chars=exclude_chars)
        # if we read a number, return it
        if str(heat).isdigit():
            return int(heat)
        return -1
    
    def get_actions_left(self) -> int:
        for _ in range(3):
            heat = self.get_actions_left_helper()
            if heat != -1:
                return heat
            time.sleep(0.1)
        return -1
    
    def get_actions_left_helper(self) -> int:
        # img_rect = self.actions_left_window.screenshot()
        # cv2.imwrite(f"actions_left_window.png", np.array(img_rect))
        heat = ocr.extract_text(self.actions_left_window, ocr.PLAIN_12, clr.WHITE, exclude_chars=exclude_chars)
        # if we read a number, return it
        if str(heat).isdigit():
            return int(heat)
        return -1

    def get_current_heat(self, loop_count: int = 3) -> int:
        for _ in range(loop_count):
            heat = self.get_current_heat_helper()
            if heat != -1:
                return heat
            time.sleep(0.1)
        return -1

    def get_current_heat_helper(self) -> int:
        # High red
        # Medium orange
        # Low green
        #img_rect = self.heat_window.screenshot()
        #cv2.imwrite(f"heat_window.png", np.array(img_rect))
        heat = ocr.extract_text(self.heat_window, ocr.PLAIN_12, colors, exclude_chars=exclude_chars)
        # if we read a number, return it
        if str(heat).isdigit():
            return int(heat)
        return -1

    def get_target_heat_range(self, current_stage: str) -> tuple[int, int]:
        # Hammer RED High - min 72 max 95
        # Grind ORANGE Medium - min 38 max 62
        # Polish GREEN Low - min 5 max 28
        if current_stage == "Hammer":
            return (71, 94)
        elif current_stage == "Grind":
            return (38, 61)
        elif current_stage == "Polish":
            return (5, 28)
        return (-1, -1)
    
    def get_current_stage(self) -> str:
        for _ in range(3):
            stage = self.get_current_stage_helper()
            if stage != "unknown":
                return stage
            time.sleep(0.1)
        return "unknown"

    def get_current_stage_helper(self) -> str:
        # save window to debug
        #img_rect = self.current_stage_window.screenshot()
        #cv2.imwrite(f"current_stage_window.png", np.array(img_rect))
        if ocr.find_text("Hammer", self.current_stage_window, ocr.PLAIN_12, red):
            return "Hammer"
        elif ocr.find_text("Grind", self.current_stage_window, ocr.PLAIN_12, orange):
            return "Grind"
        elif ocr.find_text("Polish", self.current_stage_window, ocr.PLAIN_12, green):
            return "Polish"
        return "unknown"

    def make_sword(self):
        # TODO currently if we start in the desired heat we do not click anything
        self.log_msg("Making sword...")

        # TODO being too "slow" is the other big issue, pull in bounds to fix
        current_stage = "start"
        last_action_count = self.get_actions_left()
        last_action_time = time.time()
        while self.errors < 10 and not self.no_sword_interface():
            cur_stage = self.get_current_stage()
            if bonus := self.loop_find_tag(self.bonus_color, loops=1):
                self.find_click_rectangle(bonus, "Use", color=clr.OFF_WHITE)
                time.sleep(0.5)
            elif cur_stage != "unknown" and cur_stage != current_stage:
                current_stage = cur_stage
                if rd.random_chance(0.9):
                    self.click_self_tile()
                self.fix_heat()
                self.click_active_station()
            elif not self.fix_heat():
                current_stage = self.get_current_stage()
                self.click_active_station()
            elif self.get_actions_left() != last_action_count:
                last_action_count = self.get_actions_left()
                last_action_time = time.time()
            elif time.time() - last_action_time > 20:
                self.log_msg("No actions taken for 20 seconds, retrying active station")
                current_stage = "start"
        return 
    
    def click_active_station(self):
        self.log_msg("Clicking active station...")
        if self.no_sword_interface():
            return True
        for _ in range(5):
            if self.find_click_tag(self.active_station_color, "Use", color=clr.OFF_WHITE):
                return True
            time.sleep(.1)
        self.errors += 1
        self.log_msg("Failed to click active station")
        return False
    
    def click_self_tile(self):
        self.log_msg("Clicking self tile...")
        for _ in range(5):
            if self.find_click_tag(clr.MINT, "Walk", color=clr.OFF_WHITE):
                return True
            time.sleep(.1)
        self.log_msg("AHHHHHHHHHHHHHH")
        self.mouse.move_to(self.win.game_view.get_center())
        self.mouse.click()
        self.errors += 1
        self.log_msg("Failed to click self tile")
        return False
    
    def no_sword_interface(self) -> bool:
        return self.get_current_heat(loop_count=3) == -1
