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
        search_string = "Soda ash, Bucket of sand"

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

        # self.scrape_images()
        soda_ash_img = imsearch.SCRAPER_IMAGES.joinpath("furnace", "Soda_ash_bank.png")
        sand_img = imsearch.SCRAPER_IMAGES.joinpath("furnace", "Bucket_of_sand_bank.png")
        desposit_all_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        
        furnace_color = clr.PINK
        bank_color = clr.BLUE

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            # bank 
            if not self.find_click_tag(bank_color, "Bank"):
                self.log_msg("could not click on bank!")
                break
            self.wait_till_bank_open()

            # deposit and withdraw items 
            if not self.find_click_image(desposit_all_img):
                self.log_msg("could not find deposit all button")
                break
            if not self.find_click_image(sand_img):
                self.log_msg("could not find buckets of sand")
                break
            if not self.find_click_image(soda_ash_img):
                self.log_msg("could not find soda ash")
                break

            # smelt
            if not self.find_click_tag(furnace_color, "Smelt"):
                self.log_msg("could not click on furnace!")
                break
            if not self.wait_till_interface():
                self.log_msg("smelting interface never opened")
                break
            self.take_break(max_seconds=3, fancy=True)
            keyboard.press("space")

            # TODO API down 
            # if not self.wait_till_inv_out_of(ids.SODA_ASH):
            #     self.log_msg("never ran out of soda ash")
            #     break

            time.sleep(17)
            self.take_break(max_seconds=3, fancy=True)

            self.update_progress((time.time() - start_time) / end_time)
            self.log_msg("")

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()


