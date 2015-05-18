from lib.extractor import Extractor
import sys


if __name__ == '__main__':
    extractor = Extractor(sys.argv[1])
    for box in extractor.boxes():
        print(box)
