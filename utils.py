"""
Misc. Utility Functions and classes

Author: kapil thangavelu <k_vertigo@objectrealms.net>
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
