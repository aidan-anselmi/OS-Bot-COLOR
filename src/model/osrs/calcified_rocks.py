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

class CalcifiedRocks(OSRSBot):
    def __init__(self):
        bot_title = "Calcified Rocks"
        description = (
            "This bot mines calcified rocks. Position your character near some rocks, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120

        self.break_length_multiplier = random.uniform(.5, 1.5)
        self.break_chance_multiplier = random.uniform(.5, 1.5)
        
        self.rock_color = clr.PINK
        self.bank_color = clr.RED
        self.path_color = clr.GREEN
        return

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

        # search_string = "Calcified deposit, Uncut sapphire, Hammer, Uncut emerald, Uncut ruby, Uncut diamond"
        search_string = "Deposit Inventory"
        image_type = ImageType.NORMAL
        destination = dest_dir

        path = scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)
        return 
    
    def main_loop(self):
        # self.scrape()

        self.test_bank = True
        if self.test_bank:
            self.empty_slot_clr = pag.pixel(*self.win.inventory_slots[-1].get_center())
        else:
            self.empty_slot_clr = pag.pixel(*self.win.inventory_slots[0].get_center())

        start_time = time.time()
        end_time = self.running_time * 60
        self.errors = 0
        while time.time() - start_time < end_time and self.errors < 10:
            if self.full_inventory():
                self.bank_and_return()
            self.mining_loop()
            self.bank_and_return()
        return 
    
    def mining_loop(self):
        self.log_msg("Starting mining loop")
        prev_xp = self.get_total_xp()
        self.mine_rock()
        time.sleep(10)

        while not self.full_inventory() and self.errors < 10:
            if self.get_total_xp() == prev_xp:
                self.errors += 1
            prev_xp = self.get_total_xp()

            if self.is_player_doing_action("Mining"):
                self.mine_rock()
                time.sleep(5)

            self.take_break(min_seconds=5, max_seconds=20, fancy=True)
        return True
    
    def bank_and_return(self):
        self.log_msg("Starting bank run")

        # get to bank deposit
        while not self.loop_find_tag(self.bank_color) and self.errors < 10:
            self.advance_path((-1, 0))
            time.sleep(5)

        self.bank()
        
        # get to mines
        while not self.loop_find_tag(self.bank_color) and self.errors < 10:
            self.advance_path((1, 0))
            time.sleep(5)

        return 
    
    def advance_path(self, dest_direction):
        self.log_msg(f"Advancing path in direction {dest_direction}")
        
        # Determine a sub-rectangle of the game view to search based on direction.
        # If dest_direction is (-1,0) we'll search the left half, (1,0) the right half.
        gv = self.win.game_view
        left, top, w, h = gv.left, gv.top, gv.width, gv.height

        # default to full game view
        search_rect = gv

        dx, dy = dest_direction
        # horizontal split
        if dx < 0:
            search_rect = Rectangle(left=left, top=top, width=w // 2, height=h)
        elif dx > 0:
            search_rect = Rectangle(left=left + w // 2, top=top, width=w - w // 2, height=h)
        # vertical split (overrides horizontal if provided)
        if dy < 0:
            search_rect = Rectangle(left=left, top=top, width=w, height=h // 2)
        elif dy > 0:
            search_rect = Rectangle(left=left, top=top + h // 2, width=w, height=h - h // 2)

        path_tiles = self.get_all_tagged_in_rect(search_rect, self.path_color)
        for tile in path_tiles:
            self.log_msg(f"Found path tile at {tile.rect}")

        if not path_tiles:
            self.errors += 1
            self.log_msg("No path tiles found to bank.")
            return False
        return self.pick_click_path_tile(path_tiles, dest_direction)
    
    def bank(self) -> bool:
        
        if not self.find_click_tag(self.bank_color, "Deposit", color=clr.OFF_WHITE):
            self.log_msg("could not click on bank deposit box")
            self.errors += 1
            return False
        self.wait_till_bank_deposit_open()

        if not self.find_click_image(imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")):
            self.log_msg("could not find deposit all button")
            self.errors += 1
            return False
        
        return True
    
    def pick_click_path_tile(self, path_tiles: list[RuneLiteObject], dest_direction: tuple[int, int]) -> bool:
        # Choose a path tile that lies in dest_direction relative to the player and click it.
        # dest_direction is a tuple like (-1,0) or (1,0) indicating desired direction.

        # reference center for player / game view
        game_center = self.win.game_view.get_center()

        candidates = []
        for tile in path_tiles:
            try:
                tile_center = tile.center()
            except Exception:
                # fallback if center() is not available
                tile_center = tile.rect.get_center()

            dx = tile_center.x - game_center.x
            dy = tile_center.y - game_center.y

            # require the tile to be generally in the requested direction
            dot = dx * dest_direction[0] + dy * dest_direction[1]
            if dot <= 250:
                continue

            # ignore tiles that are very close to the player
            dist = math.hypot(dx, dy)
            if dist < 250:
                continue

            candidates.append(tile)

        if not candidates:
            return False

        # prefer tiles furthest along the direction (by dot), tie-break by distance
        # candidates.sort(key=lambda t: (t[1], t[2]), reverse=True)

        # pick a random candidate
        chosen = random.choice(candidates)
        self.log_msg(f"Clicking path tile at {chosen.rect}")

        # click the chosen tile (expecting a "Walk here" mouseover)
        if not self.find_click_rectangle(chosen.rect, "Walk here", clr.OFF_WHITE):
            self.log_msg("Could not click selected path tile")
            self.errors += 1
            return False

        return True
    
    def mine_rock(self):
        rocks = self.get_all_tagged_in_rect(self.win.game_view, self.rock_color)
        if not rocks:
            self.log_msg("No calcified rocks found.")
            return False
        
        rock = self.biased_reverse_pick(rocks)
        self.find_click_rectangle(rock.rect, clr.OFF_WHITE, "Mine")
        time.sleep(3)
        return True
    
    def biased_reverse_pick(items):
        # weights: first item gets biggest weight, last gets smallest
        weights = [(len(items) - i)**1.5 for i in range(len(items))]   # e.g. [1,2,3,4,...]
        weighted_items = list(zip(items, weights))

        for item, weight in reversed(weighted_items):
            if random.random() < (weight / sum(w for _, w in weighted_items)):
                return item

        # fallback if nothing hits
        return items[0]
    
    # Your inventory is too full to hold any more
    def full_inventory(self) -> bool:
        if self.test_bank:
            return pag.pixel(*self.win.inventory_slots[0].get_center()) != self.empty_slot_clr
        return pag.pixel(*self.win.inventory_slots[-1].get_center()) != self.empty_slot_clr
