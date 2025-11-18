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


class OSRSGlassBlower(OSRSBot):
    def __init__(self):
        bot_title = "glass blower"
        description = "blows glass"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 254

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
        destination = scraper.DEFAULT_DESTINATION.joinpath("items")
        
        search_string = "Molten glass, Maple logs"        
        scraper.search_and_download(
            search_string=search_string,
            image_type=ImageType.BANK,
            destination=destination,
            notify_callback=self.log_msg)

        search_string = "Unpowered orb, Glassblowing pipe"
        scraper.search_and_download(
            search_string=search_string,
            image_type=ImageType.NORMAL,
            destination=destination,
            notify_callback=self.log_msg)
        return 

    def main_loop(self):
        # Setup APIs
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        api_m.get_inv

        self.scrape_images()
        # molten_glass_img = imsearch.SCRAPER_IMAGES.joinpath("items", "Molten_glass_bank.png")
        molten_glass_img = imsearch.SCRAPER_IMAGES.joinpath("items", "Maple_logs_bank.png")
        close_bank_img = imsearch.BOT_IMAGES.joinpath("bank", "close_bank.png")
        
        bank_color = clr.BLUE

        player_data = api_s.get_player_data()
        self.log_msg("player data - " + str(player_data))
        self.stop()
        #glass_pipe_rectangle = self.win.inventory_slots[0]

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        errors = 0
        while time.time() - start_time < end_time and errors < 10:

            # bank
            if not self.is_bank_open():
                if not self.find_click_tag(bank_color, "Bank", clr.OFF_WHITE):
                    self.log_msg("could not click on bank!")
                    errors += 1
                    continue
            self.wait_till_bank_open()
            self.take_break(max_seconds=.8, fancy=True)

            # deposit items 
            self.find_click_rectangle(self.win.inventory_slots[1], "Deposit-All")
            self.log_msg("deposited orbs.")
            self.take_break(max_seconds=.4, fancy=True)

            # withdraw items 
            if not self.find_click_image(molten_glass_img):
                self.log_msg("could not find molten glass.")
                errors += 1
                continue
            self.take_break(max_seconds=.5, fancy=True)

            # close bank
            if not self.find_click_image(close_bank_img):
                self.log_msg("could not close the bank.")
                errors += 1
                continue
            self.take_break(max_seconds=.5, fancy=True)

            self.find_click_rectangle(self.win.inventory_slots[0], "Use")
            self.take_break(max_seconds=.8, fancy=True)
            self.find_click_rectangle(self.win.inventory_slots[1], "Use")
            self.wait_till_interface()
            self.take_break(max_seconds=.5, fancy=True)
            keyboard.press("space")
            

            time.sleep(49)
            self.take_break(max_seconds=30, fancy=True)

            self.update_progress((time.time() - start_time) / end_time)
            self.log_msg(f"num errors = {errors}")

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.stop()
        


