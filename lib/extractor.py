from convert import Convert
from asset import Asset
from gridfinder import GridFinder
from . import LOGGER


class Extractor(object):
    """
    Given a PDF, calls the relevant sub-modules to do this:
    - download PDF
    - convert to PNG
    - extract cell data from grids in PNGs
    - makes cells available
    """

    def __init__(self, pdf_path):
        LOGGER.info('Extracting tables in %s' % pdf_path)
        self.pdf_path = pdf_path

    def boxes(self):
        LOGGER.info('Converting...')
        convert = Convert(self.pdf_path)
        LOGGER.info('Processing %i images...' % len(convert.images))
        for image in convert.images:
            asset = Asset(image['path'])
            LOGGER.info('asset river counts, y=[%i], x=[%i]' %
                    (len(list(asset.river_y())), len(list(asset.river_x()))))
            grid = GridFinder(asset)
            grid.process()
            if grid.cells:
                LOGGER.info('Found %s cells', len(grid.cells))
                yield {
                    'boxes': grid.cells,
                    'meta': image
                }
            else:
                LOGGER.info('Found no cells')
