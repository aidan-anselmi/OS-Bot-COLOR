import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.imagesearch as imsearch
from utilities.sprite_scraper import SpriteScraper, ImageType
import keyboard


class OSRSSandAshSmelter(OSRSBot):
    def __init__(self):
        bot_title = "sand ash smelter"
        description = "smelts sand and ash into molten glass at edgeville"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1

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
        search_string = "Soda ash, Bucket of sand, Deposit inventory"
        image_type = ImageType.BANK
        destination = scraper.DEFAULT_DESTINATION.joinpath("furnace")
        scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)
        return 

    def main_loop(self):
        # Setup APIs
        self.api_m = MorgHTTPSocket()
        # api_s = StatusSocket()

        self.scrape_images()
        soda_ash_img = imsearch.BOT_IMAGES.joinpath("furnace", "soda_ash.png")
        sand_img = imsearch.BOT_IMAGES.joinpath("furnace", "bucket_of_sand.png")
        deposit_all_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_all.png")

        furnace_color = clr.PINK
        bank_color = clr.BLUE

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # bank
            if self.api_m.get_is_player_idle():
                if bank := self.get_nearest_tag(bank_color):
                    self.mouse.move_to(bank.random_point())
                    if not self.mouseover_text(contains="Bank"):
                        continue
                    self.mouse.click()
            self.wait_till_bank_open()
            self.take_break(max_seconds=1, fancy=True)
            
            # deposit and get items 
            self.click_deposit_all()
            self.find_click_image(sand_img)
            self.find_click_image(soda_ash_img)
            self.bank_close()
            self.take_break(max_seconds=1, fancy=True)

            #smelt
            if self.api_m.get_is_player_idle():
                if furnace := self.get_nearest_tag(furnace_color):
                    self.mouse.move_to(furnace.random_point())
                    if not self.mouseover_text(contains="Smelt"):
                        continue
                    self.mouse.click()
                    self.wait_till_interface()
                    self.take_break(max_seconds=1, fancy=True)
                    keyboard.press("space")
                    
            self.wait_until_idle()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def wait_until_idle(self):
        while not self.api_m.get_is_player_idle():
            time.sleep(.1)
        self.take_break(max_seconds=1, fancy=True)
        return 


    def find_click_image(self, img):
        if deposit_all := imsearch.search_img_in_rect(img, self.win.game_view):
                self.mouse.move_to(deposit_all.random_point())
                self.mouse.click()
        self.take_break(max_seconds=1, fancy=True)
        return 