from __future__ import print_function

import os
from distutils import log
from collections import defaultdict

from _ExtMaker.ObjectTypes import function, UNHANDLED_GL_TYPES
from _ExtMaker.includes.glad_related import GLAD_RELATED_PXD


def makePXD(funcs, types, dest, announce, api, enums):
    pxdPath = os.path.join(dest, 'c{}.pxd'.format(api.upper()))
    announce('Generating {}...'.format(pxdPath), log.INFO)

    with open(pxdPath, 'w') as pxdFile:
        print('from libc.stdint cimport *', file=pxdFile)
        print('cdef extern from \'glad{}.h\' nogil:'.format('_' + api if api != 'gl' else ''), file=pxdFile)
        if api == 'gl':
            print('    # GLAD RELATED >>\n{}'.format(GLAD_RELATED_PXD), file=pxdFile)

        print('    # TYPES >>\n', file=pxdFile)
        print('    ctypedef bint bool', file=pxdFile)
        print('    ctypedef bint BOOL', file=pxdFile)
        for t in types.items():
            if 'struct' in t[1]:
                continue
            print('    ctypedef {} {}'.format(t[1], t[0].replace('(void)', '()')), file=pxdFile)

        print('\n    # FUNCTIONS >>\n', file=pxdFile)
        sortedFuncKeys = sorted(funcs)
        for fk in sortedFuncKeys:
            f = funcs[fk]
            nf = function(f, types)
            discard = False
            if nf.ret.type in UNHANDLED_GL_TYPES:
                announce('\t{} -> unhandled RETURN type ({}). Discarded.'.format(f, nf.ret.type), log.DEBUG)
                continue
            for i in range(len(nf.params)):
                p = nf.params[i]
                if p.type in UNHANDLED_GL_TYPES:
                    discard = True
                    announce('\t{} -> unhandled PARAM type ({}). Discarded.'.format(f, f.params[i].type), log.DEBUG)
                    break
            if not discard:
                print('    cdef {}'.format(nf), file=pxdFile)

        print('\n#ENUMS >>', file=pxdFile)
        eGroups = defaultdict(list)
        for e in enums:
            eGroups[e.group or api].append(e.name)
        for k in eGroups.keys():
            enumList = eGroups[k]
            print('\ncdef enum {}:'.format(k), file=pxdFile)
            for e in enumList:
                print('    {}'.format(e), file=pxdFile)