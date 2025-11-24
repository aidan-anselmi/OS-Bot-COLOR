Ideas 

Entity Tracker class:
    class that keeps track of the center of tags, and sees if the tag has moved

        # color - color of the tag we want to track 
        def TagTracker():
            self.tag_map = {}
            self.rectangle_tag_map = {}

        # tells us if a tag has moved since last poll
        # for now this color must only appear once in the given rectangle 
        def poll_tag(color, rectangle = None) -> bool:
            # initiate in map 

            # if the value has changed (or the center has moved by a value of more than 15 pixels), 
            # return true AND update map values 

            



