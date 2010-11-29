"""
Misc. Utility Functions and classes

Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

def make_lookup(seq):
    d = {}
    for s in seq:
        d[s]=None
    return d.has_key

def normalize_kv_pairs(mapping):
    res = {}

    keys = [k for k in mapping.keys() if k.startswith('key')]
    keys.sort()
    vals = [v for v in mapping.keys() if v.startswith('value')]
    vals.sort()

    pairs = zip(keys, vals)

    for k,v in pairs:
        res[mapping[k]]=mapping[v]

    return res




