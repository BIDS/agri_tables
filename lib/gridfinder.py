import numpy as np
from . import LOGGER


class GridFinder(object):

    def __init__(self, img):
        if not hasattr(img, 'dilated'):
            print('img.dilated doesnt exist')
            return
        self.img = img
        self.river_y = np.array(list(img.river_y()), dtype=np.int16)
        self.river_x = np.array(list(img.river_x()), dtype=np.int16)
        self.grids = []
        self.cells = []

    # we are dilated on X, so iterate on Y.
    def process(self):
        results = []
        dt = np.dtype([('height', np.int16, (1,)), ('xcoord', np.int16, (1,))])
        for river_y_idx, river_y_point in enumerate(self.river_y):
            try:
                # possible IndexError
                next_river_y_point = self.river_y[river_y_idx + 1]
                if next_river_y_point == river_y_point + 1:
                    # river_y_point is not the last in this river
                    pass
                else:
                    # river_y_point is the last in this river,
                    # i.e. there's data underneath now.

                    # From the Y point, for the entire width,
                    # drop a vert on every X and save
                    # the heights for each river we find.
                    # If there is a grid here, we should
                    # find a group of verts with the grid's height.
                    verts = np.array([], dtype=dt)

                    # drop a vert
                    left = None
                    right = None
                    for img_x_idx in range(self.img.dilated.shape[1]):
                        if img_x_idx in self.river_x:
                            #print('(skipping) %i is in x' % img_x_idx)
                            continue

                        # we drop a vert from this Y line all the
                        # way to the bottom, then we'll
                        # iterate down and check how much
                        # X river we can obtain.
                        vline_from_river_y_pt = self.img.dilated[
                            river_y_point:self.img.dilated.shape[0],
                            img_x_idx]

                        # get maximum amount of continuous
                        # river for this vert and make a note
                        # of it. A bunch of similarly-lengthed
                        # verts will mean we have a grid.
                        lines_with_pixels = np.where(vline_from_river_y_pt > 0)
                        if lines_with_pixels[0].size > 0:
                            height = lines_with_pixels[0][0]

                            # If we've had at least 2 interruptions
                            # on the way down, that is.
                            # (this will mean we have at least
                            # a 2 column grid.
                            # If the rivers found in this iteration
                            # is height H, then we
                            # can skip the next H river_y_points
                            # with some confidence, and we
                            # must, because there's no point dropping
                            # verts from river_y_point+1

                            verts = np.append(
                                verts,
                                np.array([(height, img_x_idx)], dtype=dt))

                            # make a note of the first and last 'sides' too
                            if not left:
                                left = img_x_idx
                            _tmp_right = img_x_idx
                    if not right:
                        right = _tmp_right

                    # cluster 'verts', and find the grid height if it exists
                    variance = np.var(verts['height'])
                    mini_rivers_d = count_mini_rivers(verts)
                    mini_rivers = mini_rivers_d['count']

                    result = {
                        'y0': river_y_point,
                        'y1': next_river_y_point,
                        'cells': mini_rivers + 1,
                        'xs': mini_rivers_d['xs'],
                        'leftmost': left,
                        'rightmost': right}
                    # a grid is at a sequence of mini_rivers
                    # (at least 2) with the largest variance
                    LOGGER.info('mini_rivers=[%i], variance=[%i]' % (mini_rivers, variance))
                    if mini_rivers >= 2 and variance >= 14: #2000:
                        self.to_cells(result)
                        self.grids.append(result)
                    results.append(result)

            except IndexError as ie:
                # we reached the end
                #print('no river line at idx %i' % idx)
                pass

        return results

    # left, top, width, height
    def to_cells(self, result):
        size = len(result['xs'])
        for idx, x in enumerate(result['xs'].astype(int)):
            top = result['y0']
            height = result['y1'] - result['y0']
            if idx == 0:  # the left most
                left = result['leftmost']
                width = x - left

                cell = {
                    'left': int(left),
                    'top': int(top),
                    'width': int(width),
                    'height': int(height)}
                self.cells.append(cell)

            elif idx == size - 1:  # right most
                # same as 'in the middle'
                left = result['xs'][idx - 1]
                width = x - left

                cell = {
                    'left': int(left),
                    'top': int(top),
                    'width': int(width),
                    'height': int(height)}
                self.cells.append(cell)

                # and the right most
                left = x
                width = result['rightmost'] - left

                cell = {
                    'left': int(left),
                    'top': int(top),
                    'width': int(width),
                    'height': int(height)}
                self.cells.append(cell)

            else:  # in the middle
                left = result['xs'][idx - 1]
                width = x - left

                cell = {
                    'left': int(left),
                    'top': int(top),
                    'width': int(width),
                    'height': int(height)}
                self.cells.append(cell)


def count_mini_rivers(X):
    count = 0
    x_mini_rivers = np.array([], dtype=np.int16)
    if (X.size > 1):
        mean = np.mean(X['height'])
        # count how many times went from False to True
        beacon = X['height'][0]  # makes no sense..........

        sub = []

        for x in X[1:]:
            if x['height'] > mean:  # if a mini river
                if beacon:
                    # if we started on a river, don't count, since it
                    # will just merge with the main river on the left
                    pass
                else:
                    sub.append(x['xcoord'])
                    beacon = True
                    count = count + 1
            else:
                if sub:
                    x_mini_rivers = np.append(x_mini_rivers, np.mean(sub))
                    sub = []
                if beacon:
                    beacon = False
                else:
                    # do nothing
                    pass
        # if we ended on a river, don't count, since it
        # will just merge with the main river on the right
        if X['height'][-1] > mean:
            count = count - 1
    return {'count': count, 'xs': np.rint(x_mini_rivers)}
