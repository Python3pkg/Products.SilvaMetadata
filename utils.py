"""
Misc. Utility Functions and classes

Author: kapil thangavelu <k_vertigo@objectrealms.net>
$Id: utils.py,v 1.2 2003/04/22 17:58:48 hazmat Exp $
"""

class StringBuffer:

    def __init__(self):
        self.buf =[]
    def write(self, data):
        self.buf.append(data)
    def getvalue(self):
        return ''.join(self.buf)

def make_lookup(seq):
    d = {}
    for s in seq:
        d[s]=None
    return d.has_key
