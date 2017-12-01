import pigo
import time  # import just in case students need
import datetime
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
        self.start_time = datetime.datetime.utcnow()
        # Our servo turns the sensor. What angle of the servo( ) method sets it straight?
        self.MIDPOINT = 89
        # YOU DECIDE: How close can an object get (cm) before we have to stop?
        self.SAFE_STOP_DIST = 30
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.HARD_STOP_DIST = 15
        self.LEFT_SPEED = 130
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.RIGHT_SPEED = 150
        # This one isn't capitalized because it changes during runtime, the others don't
        self.turn_track = 0
        # Our scan list! The index will be the degree and it will store distance
        self.next_right = True
        # alternator for left and right turn
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
        menu = {"n": ("Navigate", self.nav),
                "h": ("Restore heading", self.test_restore_heading),
                "t": ("Enc Based Turn Navigation", self.enc_turn_nav),
                "r": ("Rotate Based Turn Navigation", self.rot_turn_nav),
                "d": ("Dist", self.dist_test),
                "o": ("Detect Obstacles", self.obstacle_detect),
                "f": ("Detect Obstacles w/ 360", self.full_detect),
                "c": ("Calibrate", self.calibrate),
                "s": ("Check status", self.status),
                "q": ("Quit", quit_now),
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
            self.turn_right()  # turns 90 deg to the right
            self.to_the_direction()  # shuffle
            self.turn_around_left()  # turns 180 deg around
            self.to_the_direction()  # shuffle
            self.turn_right()  # turns 90 deg right
            self.now_kick() #
            self.turn_left()
            self.box()
            self.carlton()

    def safety_check(self):
        """completes safety sweep, doesn't dance if not safe"""
        self.servo(self.MIDPOINT)
        for x in range(4):  # completes sweep in 4 directions
            if not self.is_clear():
                print("Check Distance")
                return False  # returns false if test fails
            self.encR(6)
        print("I will not dance")
        return True  # returns true if test passes

    def turn_right(self):
        """turns robot 90 deg to the right"""
        self.encR(7)
        self.stop()

    def turn_left(self):
        """turns robot 90 deg left"""
        self.encL(7)
        self.stop()

    def turn_around_left(self):
        """turns robot 180 deg around to the left"""
        self.servo(135)
        self.encL(18)
        self.stop()

    def to_the_direction(self):
        """moves robot forward 4 times"""
        for x in range(4):
            self.encF(13)
            self.stop()

    def now_kick(self):
        """moves robot forward and back quickly like a kick"""
        for x in range(3):
            self.encF(5)
            self.encB(5)
            self.encR(3)
            self.encF(5)
            self.encB(5)
            self.encF(3)

    def carlton(self):
        """robots does the carlton dance"""
        self.encR(7)  # initial right 90 deg turn
        self.servo(45)
        self.stop()
        for x in range(5):  # moves robot left and right along with servo on a loop
            self.encL(12)
            self.servo(135)
            self.stop()
            self.encR(12)
            self.servo(45)
            self.stop()

    def box(self):
        """moves robot in a box shape"""
        for x in range(4):  # turns right, moves forward on loop
            for x in range(4):
                self.encF(10)
                self.servo(60)
                self.encR(7)
            self.turn_around_left()

    def restore_heading(self):
        """uses self.turn_track reorient to original heading"""
        print("Restoring heading!")
        if self.turn_track > 0:
            self.encL(abs(self.turn_track))
        elif self.turn_track < 0:
            self.encR(abs(self.turn_track))

    def test_restore_heading(self):
        self.encR(5)
        self.encL(15)
        self.encR(10)
        self.encR(10)
        self.encL(7)
        self.restore_heading()

    def smooth_turn(self):
        self.right_rot()
        start = datetime.datetime.utcnow()
        self.servo(self.MIDPOINT)
        while True:
            if self.dist() > 100:
                self.stop()
            elif datetime.datetime.utcnow() - start > datetime.timedelta(seconds=10):
                self.stop()
            time.sleep(.2)

    def cruise(self):
        """drive straight while path is clear"""
        print("I'm about to drive forward")
        self.fwd()
        while self.dist() > self.SAFE_STOP_DIST:
            time.sleep(.5)
        self.stop()


######## NAV METHODS #########

    def dist_test(self):
        while True:
            print(self.dist())

    def nav(self):
        """auto pilots using an alternating turn"""
        logging.debug("Starting the nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        right_now = datetime.datetime.utcnow()
        difference = (right_now - self.start_time).seconds
        print("It took you %d seconds to run this" % difference)
        while True:
            if self.dist() > self.SAFE_STOP_DIST:
                self.cruise()
            else:
                self.stop()  # stops robot
                self.encB(3)
                self.alternate_turn()
                """
                if self.next_right:  # restores heading based on turn track from previous correction direction
                    self.encR(abs(self.turn_track))
                else:   # restores heading based on turn track from previous correction direction
                    self.encL(abs(self.turn_track))
                """

    def alternate_turn(self):
        if self.next_right:  # checks if self.next_right variable is true in init method
            while self.dist() < self.SAFE_STOP_DIST:
                self.encR(2)
                time.sleep(.1)
            self.next_right = False  # changes variable to false used used
            time.sleep(.1)
            self.encR(3)
            time.sleep(.1)

        else:
            while self.dist() < self.SAFE_STOP_DIST:
                self.encL(2)
                time.sleep(.1)
            self.next_right = True  # changes variable to true when used
            time.sleep(.1)
            self.encL(3)
            time.sleep(.1)


    def enc_turn_nav(self):
        """auto pilots and attempts to maintain original heading by turning right if it
        detects and object, based on enc values"""
        logging.debug("Starting the enc_turn_nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        while True:
            self.cruise()
            if self.dist() < self.SAFE_STOP_DIST:  # detects an unsafe distance
                self.stop()

                while self.dist() < self.SAFE_STOP_DIST:  # loops to turn right by encR(1) until safe
                    self.encR(2)
                    time.sleep(.5)

                self.encR(3)  # small turn buffer to ensure the robot turns past its side
                print(self.turn_track)

                while self.dist() > self.SAFE_STOP_DIST:  # pulls forward while safe
                    self.fwd()
                    time.sleep(.05)

                self.encB(9)  # backs up
                self.stop()
                self.encL(abs(self.turn_track))  # turns back to original heading

                time.sleep(1)

    def rot_turn_nav(self):
        """auto pilots and attempts to maintain original heading by turning right if it
        detects and object, based on time values"""

        logging.debug("Starting the rot_turn_nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        while True:
            self.cruise()
            if self.dist() < self.SAFE_STOP_DIST:  # detects an unsafe distance
                self.stop()
                start = datetime.datetime.utcnow()  # records current time
                while self.dist() < self.SAFE_STOP_DIST:  # turns right until it detects a safe distance
                    self.right_rot()
                end = datetime.datetime.utcnow()  # records end time
                elapsed = (end - start).microseconds  # calculates difference in time between start and end
                print(elapsed)  # for testing

                self.stop()

            # self.encF(32)

                while elapsed < (datetime.timedelta(seconds=elapsed)).microseconds:
                    self.left_rot()

    def obstacle_detect(self):
        """scans and counts number of obstacles within sight"""
        self.wide_scan()
        found_objects = False
        object_counter = 0
        for dist in self.scan:
            if dist and dist < 50 and not found_objects:
                found_objects = True
                object_counter += 1
                # print("Object # %d found, I think" % object_counter)
            if dist and dist > 50 and found_objects:
                found_objects = False
        # print("\n----- I found %d obstacles ------\n" % object_counter)
        return object_counter

    def full_detect(self):
        total_objects = 0
        for x in range(3):
            self.stop()
            total_objects += self.obstacle_detect()
            self.stop()
            self.encL(5)
            self.stop()
        print("\n----I see %d total objects----\n" % total_objects)

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
