import cPickle
import glob
import os



class EventLoop:
    """Main driving class for looping through coincident signals of different TODs"""
    def __init__(self):
        self._routines = []
        self._veto = False
        self._store = DataStore()  # initialize data store
        self._sh = None  # sample handler
        self._tod_id = None
        
    def add_routine(self, routine):
        """Add a routine to the event loop"""
        self._routines.append(routine)
        print '[INFO] Added routine: %s' % routine.__class__.__name__
        routine.add_context(self)  # make event loop accessible in each routine
        
    def add_handler(self, sh):
        """Add a sample handler to the event loop"""
        self._sh = sh
        
    def get_store(self):
        """Access the shared data storage"""
        return self._store
    
    def fetch_files(self):
        return self._sh.fetch_files()
    
    def initialize(self):
        """Initialize all routines"""
        for routine in self._routines:
            routine.initialize()
    
    def execute(self):
        """Execute all routines"""
        for routine in self._routines:
            # check veto signal, if received, skip subsequent routines
            if self._veto:
                break
            else:
                routine.execute()
        self._veto = False
    
    def finalize(self):
        """Finalize all routines"""
        for routine in self._routines:
            routine.finalize()
    
    def run(self,start,end):
        files = self.fetch_files()  # fetch all files
        
        self.initialize()
        for filename in files[start:end]:
            # get tod_id
            self._tod_id = int(os.path.basename(filename).split(".")[0])
            with open(filename, "r") as f:
                print '[INFO] Working on %s' % filename
                cosig = cPickle.load(f)  # load coinsident signal from each file
                self.get_store().set("cosig", cosig)  # store it in shared memory
            self.execute()
        self.finalize()
        
    def veto(self):
        """Veto a TOD from subsequent routines"""
        self._veto = True
    
    def get_id(self):
        return self._tod_id

        
class Routine:
    def __init__(self):
        self._context = None
    
    def initialize(self):
        pass
    
    def execute(self):
        pass
    
    def finalize(self):
        pass
    
    def veto(self):
        self.get_context().veto()
        
    def add_context(self, context):
        self._context = context
        
    def get_context(self):
        return self._context

    
    
class SampleHandler:
    def __init__(self, depot=None, postfix="pickle"):
        self._depot = depot
        self._postfix = postfix
        self._files = None
        self._metadata = None
    
    def fetch_files(self):
        self._files = glob.glob(self._depot + "*." + self._postfix)
        return self._files
        
    def load_metadata(self):
        """Load metadata if there is one"""
        metadata_path = self._depot + ".metadata"
        if os.path.isfile(matadata_path):
            with open(self._depot + ".metadata", "r") as meta:
                self._metadata = cPickle.load(meta)
    
    def get_metadata(self):
        return self._metadata
    
    
    
class DataStore:
    """Cache class for event loop"""
    def __init__(self):
        self._store = {}
    
    def get(self, key):
        """Retrieve an object based on a key
        @par: 
            key: str
        @ret:   
            Object of an arbitrary type associated with the key
            or None if no object is associated with the key"""
        if key in self._store:
            return self._store[key]
        else:
            return None
    
    def set(self, key, obj):
        """Save an object with a key
        @par:
            key: str
            obj: a object of arbitrary type
        @ret: nil"""
        self._store[key] = obj
        
