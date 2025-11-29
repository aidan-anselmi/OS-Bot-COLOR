import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.imagesearch as imsearch
from utilities.sprite_scraper import SpriteScraper, ImageType
from pynput.keyboard import Key, Controller
from pathlib import Path
import pyautogui as pag


class OSRSGlassBlower(OSRSBot):
    def __init__(self):
        bot_title = "glass blower"
        description = "blows glass"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 90

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def scrape_images(self):
        scraper = SpriteScraper()

        # set destination directory to src/images/bot/items (project-relative)
        dest_dir = Path(__file__).resolve().parents[2].joinpath("images", "bot", "items")
        # make sure directory exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        search_string = "Yew longbow (u), Bow string"
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
        keyboard = Controller()

        self.scrape_images()
        bank_color = clr.BLUE

        bow_img = imsearch.BOT_IMAGES.joinpath("items", "Yew_longbow_(u)_bank.png")
        string_img = imsearch.BOT_IMAGES.joinpath("items", "Bow_string_bank.png")

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        errors = 0
        items_made = 0
        while time.time() - start_time < end_time and errors < 10 and items_made < 2380:

            # bank
            if not self.is_bank_open():
                if not self.find_click_tag(bank_color, "Bank", clr.OFF_WHITE):
                    self.log_msg("could not click on bank!")
                    errors += 1
                    continue
            self.wait_till_bank_open()
            self.take_break(max_seconds=.8, fancy=True)

            # deposit items 
            #self.find_click_rectangle(self.win.inventory_slots[0], "Deposit-All")
            self.find_click_image(imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png"))
            self.log_msg("deposited orbs.")
            self.take_break(max_seconds=1, fancy=True)

            # withdraw items 
            if not self.find_click_image(bow_img):
                self.log_msg("could not find molten glass.")
                errors += 1
                continue
            self.take_break(max_seconds=1, fancy=True)
            if not self.find_click_image(string_img):
                self.log_msg("could not find molten glass.")
                errors += 1
                continue
            self.take_break(max_seconds=1, fancy=True)

            # close bank
            pag.press('esc')
            self.take_break(max_seconds=1, fancy=True)

            self.find_click_rectangle(self.win.inventory_slots[13], "Use")
            self.take_break(max_seconds=1, fancy=True)
            self.find_click_rectangle(self.win.inventory_slots[14], "Use")
            self.wait_till_interface()
            self.take_break(max_seconds=1, fancy=True)
            keyboard.press(Key.space)
            self.log_msg("Making product...")
            items_made += 14

            time.sleep(17)
            if rd.random_chance(.95):
                self.take_break(max_seconds=5, fancy=True)
            else:
                self.take_break(min_seconds=20, max_seconds=60, fancy=True)

            self.update_progress((time.time() - start_time) / end_time)
            self.log_msg(f"num errors = {errors}")

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.stop()
        


