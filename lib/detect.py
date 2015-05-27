"""
First run in samples: 
mogrify -format png -density 150 input.pdf -quality 90  -- *.pdf
"""

import cv2
import os
import numpy as np
from matplotlib import pylab

def peakdetect(v, delta, x=None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    maxtab = []
    mintab = []
       
    if x is None:
        x = np.arange(len(v))
    
    v = np.asarray(v)
    
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    
    if not np.isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    
    mn, mx = np.Inf, -np.Inf
    mnpos, mxpos = np.NaN, np.NaN
    
    lookformax = True
    
    for i in np.arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True
 
    return np.array(maxtab), np.array(mintab)
 


datasets_dir = "../samples"
filenames = [f for f in sorted(os.listdir(datasets_dir)) if f.lower().endswith(".png")]
for i, filename in enumerate(filenames):
    print i, filename
    filename = os.path.join(datasets_dir, filename)
    # filename = '../samples/aa_test.png'
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    results = cv2.findContours(thresholded, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(results) == 2:
        contours = results[0]
    else:
        contours = results[1]
    draw_image = ~image.copy()
    newimage = np.zeros(thresholded.shape, dtype=np.uint8)

    boxes = [cv2.boundingRect(contour) for contour in contours]
    widths = [box[2] for box in boxes]
    typical_width = np.median(widths)
    merge_width = int(typical_width)

    # merge letters to form word blocks
    for box in boxes:
       if box[2] > 5 * typical_width or box[3] > 5 * typical_width:
            continue
       cv2.rectangle(newimage, (box[0] - merge_width, box[1]), (box[0] + box[2] + merge_width, box[1] + box[3]), 255, -1)

    # refind contours in merged line image
    boximage = newimage.copy()
    results = cv2.findContours(newimage, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(results) == 2:
        contours = results[0]
    else:
        contours = results[1]
    # make histogram of x coverage of word boxes.
    hist_x1 = np.zeros(image.shape[1])
    for contour in contours:
        box = cv2.boundingRect(contour)
        hist_x1[box[0]:box[0]+box[2]] += 1

    max_x = np.max(hist_x1)
    line_x = np.where(hist_x1 > max_x * 0.6)
    maxtab, mintab = peakdetect(hist_x1, np.max(hist_x1) * 0.2)

    for i, x in maxtab:
        x = int(i) 
        cv2.line(draw_image, (x, 0), (x, 2000), (0, 0, 255), 2)
    draw_image[boximage != 0, 0] = 255

    cv2.imshow("process", draw_image)
    pylab.clf()
    pylab.plot(hist_x1)
    pylab.plot(maxtab[:, 0], maxtab[:, 1], 'o')
    pylab.ion()
    pylab.show()

    while cv2.waitKey(0) != 27:
        pass
