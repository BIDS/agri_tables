import numpy as np

from skimage import io, img_as_bool
from skimage.filters import threshold_adaptive
from skimage.color import rgb2gray

from scipy import ndimage

from dilation import Dilation


class Asset(object):
    """An asset loader which loads an image from a URL,
    and adds some convenience data.

    """

    def __init__(self, img_url, dilation=None):
        self.image = io.imread(img_url)
        self.gray = rgb2gray(self.image)
        self.width = len(self.gray[0])
        self.height = len(self.gray)

        # binarise
        self.binary = threshold_adaptive(self.gray, 41, offset=0.1)

        # invert (uninteresting stuff must be black)
        # TODO cater for images where the features
        # are lighter than the background
        self.inverted = np.invert(self.binary)

        # dilate the features
        if not dilation:
            dilation = Dilation(which='x', iterations=1)

        self.dilated = ndimage.binary_dilation(
            self.inverted,
            structure=dilation.struct,
            iterations=dilation.iterations).astype(self.inverted.dtype)

        self.dilated_bool = img_as_bool(self.dilated)
        # find rivers in-between the dilated blobs

    def centroids(self):
        lbl, num = ndimage.label(self.dilated)
        self.centroids = ndimage.measurements.center_of_mass(
            self.dilated,
            lbl,
            range(1, num+1))

        # transpose points into list of X and list of Y
        xy = np.transpose(self.centroids)
        self.x_centers = xy[1]
        self.y_centers = xy[0]

    def river_y(self):
        # yield those points on the axis which is a river
        for idx, row in enumerate(self.dilated_bool):
            if not np.any(row):  # not any = all black = a river
                yield idx

    def river_x(self):
        # yield those points on the axis which is a river
        for idx, row in enumerate(np.transpose(self.dilated_bool)):
            if not np.any(row):  # not any = all black = a river
                yield idx
