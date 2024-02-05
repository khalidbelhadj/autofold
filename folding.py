import time
import PicoRobotics

# The default angle to fold the panels.
ANGLE = 160
STARTING_ANGLE = 10

# The list of panel names, numbered by their index i.e. bottom = 1, left = 2 etc.
PANELS = ["bottom", "left", "right", "middle", "top"]

board = PicoRobotics.KitronikPicoRobotics()

INFO = 0
ERROR = 1

def log(level: int, message: str, *args: Any):
    if level == INFO:
        message = "[INFO] " + message
    elif level == ERROR:
        message = "[ERROR] " + message
    else:
        raise ValueError("Level " + str(level) + "not found")
    print(message, *args)


def degrees(angle: int):
    """
    Interpolates the angle to be between 0-180 for a 270 degree servo.
    """
    return (angle / 270) * 180


def fold(panel: str, angle: int=ANGLE):
    """
    Folds the given panel. Fold angle default to ANGLE.
    """
    servo = 0

    try:
        servo = PANELS.index(panel) + 1
    except ValueError:
        log(ERROR, panel, "is not a valid panel. Use one of the follwing:", str(PANELS))
        return

    log(INFO, "Folding " + panel + " panel...")
    board.servoWrite(servo, degrees(angle))
    time.sleep(0.75)
    board.servoWrite(servo, degrees(STARTING_ANGLE))
    time.sleep(0.75)
    log(INFO, "Folding done")


def reset_servo_angles():
    """
    Sets the angle to STARTING_ANGLE for all the servos.
    """
    log(INFO, "Resetting servo angles to " + str(STARTING_ANGLE) + "...")
    for i in range(len(PANELS)):
        board.servoWrite(i + 1, STARTING_ANGLE)
        time.sleep(1)
    log(INFO, "Resetting done")


def main():
  fold("right")
        
if __name__ == "__main__":
    main()

 