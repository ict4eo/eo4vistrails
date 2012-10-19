# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
###
### This full package extends VisTrails, providing GIS/Earth Observation
### ingestion, pre-processing, transformation, analytic and visualisation
### capabilities . Included is the ability to run code transparently in
### OpenNebula cloud environments. There are various software
### dependencies, but all are FOSS.
###
### This file may be used under the terms of the GNU General Public
### License version 2.0 as published by the Free Software Foundation
### and appearing in the file LICENSE.GPL included in the packaging of
### this file.  Please review the following to ensure GNU General Public
### Licensing requirements will be met:
### http://www.opensource.org/licenses/gpl-license.php
###
### If you are unsure which license is appropriate for your use (for
### instance, you are interested in developing a commercial derivative
### of VisTrails), please contact us at vistrails@sci.utah.edu.
###
### This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
### WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
###
#############################################################################
"""This module forms part of the eo4vistrails capabilities. It is used to
provide common utility functions for working with lists.
"""


def uniqify(seq, idfun=None):
    """Return unique sequence, preserving the sequence order.

    See:
        http://www.peterbe.com/plog/uniqifiers-benchmark (f5)
   """
    if idfun is None:
        def idfun(x):
            return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


def get_filter(items):
    """Create a list of values from numeric ranges defined in a string.

    Accepts:

    A single string, with a specification that uses the following syntax:
     *  N: a single integer; or a single Excel column letter
     *  N-M: a range of integers; or a range of Excel column letters
     *  N, M, ...: multiple different single/range values

    Returns:
     *  A list of integers
    """

    def to_int(index):
        s = 0
        pow = 1
        try:
            return int(index)
        except:
            pass
        for letter in index[::-1]:
            d = int(letter, 36) - 9
            s += pow * d
            pow *= 26
        # excel starts column numeration from 1
        return s

    list = []
    if items:
        try:
            item_list = items.split(',')
            for item in item_list:
                if '-' in item:
                    _range = item.split('-')
                    _short = [x for x in range(to_int(_range[0]),
                                               to_int(_range[1]) + 1)]
                    list = list + _short
                else:
                    list.append(to_int(item))
        except Exception, e:
            self.raiseError('Cannot process output specifications: %s' % \
                            str(e))
            return []
    if list:
        return set(list)  # remove duplicates
    else:
        return list  # empty
