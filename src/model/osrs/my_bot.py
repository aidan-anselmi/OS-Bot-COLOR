import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.random_util as rd
import utilities.color as clr
import utilities.imagesearch as imsearch


class OSRSMyBot(OSRSBot):
    def __init__(self):
        bot_title = "my bot"
        description = "creating your first bot"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.take_breaks = True 

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("take_breaks", "Take breaks?", ["Yes", "No"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            elif option == "multi_select_example":
                self.log_msg(f"Multi-select example: {options[option]}")
            elif option == "menu_example":
                self.log_msg(f"Menu example: {options[option]}")
            elif option == "take_breaks":  # <-- Add this line
                self.take_breaks = options[option] == "Yes" # <-- Add this line
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.`
          operator to access their functions.
        """
        # Setup APIs
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        tinderbox_img = imsearch.BOT_IMAGES.joinpath("items", "tinderbox.png")

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # 5% chance to take a break between clicks
            if rd.random_chance(probability=0.05) and self.take_breaks:
                self.take_break(max_seconds=15, fancy=True)

            
            

            # If we have 3 or more logs, drop them
            log_slots = api_m.get_inv_item_indices(ids.logs)
            if len(log_slots) >= 3:
                self.drop(log_slots)
                time.sleep(1)

            # If we are idle, click on a tree
            if api_m.get_is_player_idle():
                if tree := self.get_nearest_tag(clr.PINK):
                    self.mouse.move_to(tree.random_point())
                    if not self.mouseover_text(contains="Chop"):
                        continue
                    self.mouse.click()
            time.sleep(1)

            if tinderbox := imsearch.search_img_in_rect(tinderbox_img, self.win.control_panel):
                self.mouse.move_to(tinderbox.random_point())

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()