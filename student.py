import pigo
import time  # import just in case students need
import random

# setup logs
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/PnR-Final/log_robot.log"  # don't forget to make this file!
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)


class Piggy(pigo.Pigo):
    """Student project, inherits teacher Pigo class which wraps all RPi specific functions"""

    def __init__(self):
        """The robot's constructor: sets variables and runs menu loop"""
        print("I have been instantiated!")
        # Our servo turns the sensor. What angle of the servo( ) method sets it straight?
        self.MIDPOINT = 89
        # YOU DECIDE: How close can an object get (cm) before we have to stop?
        self.SAFE_STOP_DIST = 30
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.HARD_STOP_DIST = 15
        self.LEFT_SPEED = 110
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.RIGHT_SPEED = 120
        # This one isn't capitalized because it changes during runtime, the others don't
        self.turn_track = 0
        # Our scan list! The index will be the degree and it will store distance
        self.scan = [None] * 180
        self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
        # let's use an event-driven model, make a handler of sorts to listen for "events"
        while True:
            self.stop()
            self.menu()

    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values
        # You may change the menu if you'd like to add an experimental method
        menu = {"n": ("Navigate forward", self.nav),
                "d": ("Dance", self.dance),
                "c": ("Calibrate", self.calibrate),
                "s": ("Check status", self.status),
                "q": ("Quit", quit_now)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = raw_input("Your selection: ")
        # activate the item selected
        menu.get(ans, [None, error])[1]()

    # YOU DECIDE: How does your GoPiggy dance?
    def dance(self):
        """executes a series of methods that add up to a compound dance"""
        print("\n---- LET'S DANCE ----\n")
        ##### WRITE YOUR FIRST PROJECT HERE
        if self.safety_check():
            # self.turn_right()  # turns 90 degrees
            # self.to_the_direction()  # shuffle
            # self.turn_around_left()  # turns 180 degrees
            # self.to_the_direction()  # shuffle
            # self.turn_right()  # turns 90 degrees
            # self.now_kick()
            # self.turn_left()
            self.carlton()

    def safety_check(self):
        self.servo(self.MIDPOINT)
        for x in range(4):
            if self.dist() < self.SAFE_STOP_DIST:
                return False
            else:
                self.encR(6)
        return True


    def turn_right(self):
        self.encR(7)
        self.stop()

    def turn_left(self):
        self.encL(7)
        self.stop()

    def turn_around_left(self):
        self.servo(135)
        self.encL(18)
        self.stop()

    def to_the_direction(self):
        """sub routine of dance method"""
        for x in range(4):
            self.encF(13)
            self.stop()

    def now_kick(self):
        for x in range(3):
            self.encF(5)
            self.encB(5)
            self.encR(3)
            self.encF(5)
            self.encB(5)
            self.encF(3)

    def carlton(self):
        self.encR(7)
        self.servo(45)
        self.stop()
        for x in range(5):
            self.encL(12)
            self.servo(135)
            self.stop()
            self.encR(12)
            self.servo(45)
            self.stop()




    def nav(self):
        """auto pilots and attempts to maintain original heading"""
        logging.debug("Starting the nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")


####################################################
############### STATIC FUNCTIONS

def error():
    """records general, less specific error"""
    logging.error("ERROR")
    print('ERROR')


def quit_now():
    """shuts down app"""
    raise SystemExit

##################################################################
######## The app starts right here when we instantiate our GoPiggy


try:
    g = Piggy()
except (KeyboardInterrupt, SystemExit):
    pigo.stop_now()
except Exception as ee:
    logging.error(ee.__str__())
