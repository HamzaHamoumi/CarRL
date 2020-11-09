import sys
from Controller import Controller


if __name__ == '__main__':
    if len(sys.argv) == 2:
        controller = Controller(sys.argv[1])
    elif len(sys.argv) == 3:
        controller = Controller(sys.argv[1], sys.argv[2])
    else:
        controller = Controller()
    controller.start()
