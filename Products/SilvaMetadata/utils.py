# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
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

    keys = [k for k in list(mapping.keys()) if k.startswith('key')]
    keys.sort()
    vals = [v for v in list(mapping.keys()) if v.startswith('value')]
    vals.sort()

    pairs = list(zip(keys, vals))

    for k,v in pairs:
        res[mapping[k]]=mapping[v]

    return res




