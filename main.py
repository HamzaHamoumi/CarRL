import sys
from Controller import Controller


if __name__ == '__main__':
    if len(sys.argv) > 1:
        controller = Controller(sys.argv[1])
    else:
        controller = Controller()
    controller.start()
