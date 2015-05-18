import subprocess as sp
import os
import shutil
import re
from . import LOGGER


class Convert(object):
    """
    Converts PDF to PNGs, one PNG per page.
    Cached in a directory called 'cache'.

    """

    PATTERN = re.compile(r'inputfile([0-9]+)\.png')

    def __init__(self, pdf_path):
        """Given pdf_path, e.g. samples/some_report.pdf, creates the following:
        A cache directory: .cache/some_report.pdf/
        A copy of the PDF: .cache/some_report.pdf/inputfile.pdf

        The copy is purely for the Linux utility 'convert' which will
        create the PNG files in the same location. This keeps the
        original directory (samples) clean.
        """
        filename = os.path.basename(pdf_path)
        LOGGER.info('PDF filename=%s' % filename)

        cache_directory = 'cache/%s' % (filename[:-4])  # drop .pdf
        if not os.path.exists(cache_directory):
            os.makedirs(cache_directory)
            LOGGER.info('Created cache directory: %s' % cache_directory)
        else:
            LOGGER.info('Existing cache directory: %s' % cache_directory)

        pdf_cached_path = '%s/inputfile.pdf' % (cache_directory)
        shutil.copyfile(pdf_path, pdf_cached_path)

        self.workdir = cache_directory
        self.pdf = pdf_cached_path

        self.images = []
        self._convert()

    def _convert(self,):
        img = self.pdf.replace('.pdf', '.png')
        LOGGER.info('Converting PDF=[%s] to image=[%s]' % (self.pdf, img))
        conversion = sp.Popen(
            ['convert', self.pdf, img],
            close_fds=True)
        conversion.wait()

        LOGGER.info('Done converting PDF to PNG')
        contents = os.listdir(self.workdir)

        if len(contents) == 2:
            # only 1 page
            self.images.append({
                'path': '%s/%s' % (self.workdir, 'inputfile.png'),
                'page_number': 1 
            })
        else:
            for fn in contents:
                LOGGER.info(fn)
                if '.png' in fn:
                    self.images.append({
                        'path': '%s/%s' % (self.workdir, fn),
                        'page_number': Convert.PATTERN.search(fn).group(1)
                    })
