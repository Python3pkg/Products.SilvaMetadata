"""
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2003
$Id: ChangeSet.py,v 1.1 2003/04/22 14:45:30 hazmat Exp $
"""

from OFS.Folder import Folder
from time import time
from BTrees.OIBTree import OISet
from BTrees.Length import Length

class ChangeLog(Folder):

    all_meta_types = ()
    
    meta_type = 'ChangeLog'

    manage_options = (
        
        {'label':'ChangeLog',
         'action':'log_overview'},

        {'label':'Metadata Set',
         'action':'../overview'},
        )

    security = ClassSecurityInfo()

    log_overview = DTMLFile('', globals())

    def __init__(self, id):
        self.id = id
        self._records = OISet()
        self._record_length = Length(0)

    security.declarePrivate('attachHistory')
    def attachEntry(self, history):
        hid = str(self._record_length())
        history.id = hid
        self._records.insert(history)
        self._record_length.change(1)
        
    security.declareProtected(Permissions.view_management_screens, 'getHistories')
    def getEntries(self):
        return tuple(self._records)

    security.declarePrivate('getLastTime')
    def getLastTime(self):
        if self._record_length() == 0:
            return None
        return self._records[self._record_length()-1].bobobase_modification_time()

    def __bobo_traverse__(self, REQUEST, name=None):

        try:
            hid = int(name)
            return self._records[hid].__of__(self)
        except:
            return getattr(self, name)

InitializeClass(ChangeLog)


class LogEntry(SimpleItem):

    meta_type = 'Log Entry'

    manage_options = ()

    security = ClassSecurityInfo()    

    index_html = DTMLFile('ui/LogEntryView', globals())
    
    def __init__(self, id):
        self.id = id
        self.creation_time = DateTime()
        self.timeTime = str(int(self.creation_time.timeTime()))
        self.logs = []
        self.statistics = None
        
    def recordStatistics(self, stats_display):
        self.statistics = stats_display

    def log(self, msg, level):
        self.logs.append(msg)

    security.declarePublic('row_display')
    def row_display(self):
        return 'Deployed %s (<a href="%s">More Info</a>)'%(
            self.creation_time.fCommonZ(),
            self.id
            )

InitializeClass(LogEntry)

class MetadataChangeLog:
    pass

class Change:
    pass

class ChangeSetCollection:
    pass

class ChangeSet:

    def __init__(self, start_idx, change_data):
        self.start_idx = start_idx
        self.change_data = change_data

    def close(self, end_idx):
        self.end_idx = end_idx
