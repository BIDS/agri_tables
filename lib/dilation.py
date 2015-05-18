import numpy as np


class Dilation(object):

    def __init__(self, which='both', iterations=1):
        if which == 'both':
            self.struct = np.array([
                [0, 1, 0],
                [1, 1, 1],
                [0, 1, 0]
            ])
        elif which == 'x':
            self.struct = np.array([
                [0, 0, 0],
                [1, 1, 1],
                [0, 0, 0]
            ])
        elif which == 'y':
            self.struct = np.array([
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0]
            ])

        self.iterations = iterations
