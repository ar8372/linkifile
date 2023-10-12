
import pandas as pd
import time 
import concurrent.futures
from .utils import search , load_data, save_data, true_random, fix_random

class Linker:
    """  
    Linker class for linking data from a source file to a destination file based on a web search query.

    Parameters
    ----------
    source_file : str
        The path to the source file containing data to be linked.
    coln_pairs : list
        A list of column names used for linking data.
    destination_file : str, optional
        The path to the destination file where the linked data will be stored. If not provided, the source file is modified in place.

    Attributes
    ----------
    source_file : str
        The path to the source file.
    coln_pairs : list
        A list of column names for linking data.
    destination_file : str
        The path to the destination file.
    source_type : str
        The file type (e.g., 'csv', 'xlsx') of the source file.
    destination_type : str
        The file type of the destination file.
    valid_extensions : list
        A list of valid file extensions (e.g., 'csv', 'xlsx').

    Methods
    -------
    call_search(x)
        Performs a web search using the specified query (`x`) and returns the search result or an alternate text if no result is found.
    populate(query=None, sleep_interval=10, alternate_text="Not Found", speedup=False, verbose=1)
        Populates the destination file with search results based on the specified query. Utilizes multithreading for faster execution if `speedup` is set to `True`.
    query(queries, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5, alternate_text="Not Found", speedup=False, verbose=1)
        Executes one or more search queries and returns the search results.
    _initialize(lang, proxy, advanced, sleep_interval, timeout, alternate_text, speedup, verbose)
        Initializes query-related parameters.
    Examples
    --------
    To link data from a source file to a destination file using the `Linker` class, you can follow this example:

    from linkifile import Linker
    #Task Type1
    l = Linker(source_file= "a.csv", coln_pairs=["Compnay Name", "Website Link"], destination_file="b.csv")
    Ex:-
    l.populate(query= "{{x}} baby product company official website", verbose=1)
    Search Query:=> Graco baby product company official website
    result:https://www.gracobaby.com/about-us.html

    l.populate(query= "{{x}} industry official website", verbose=1)
    Search Query:=> Graco is a baby product company
    result:https://www.graco.com/us/en.html

    #Taks Type2
    l = Linker()
    l.query("apple")
    Result: https://www.apple.com/in/

    This code will execute the linking process, search for information related to the specified query, and populate the destination file with the search results.

    """
    def __init__(self, source_file=None, coln_pairs=None, destination_file=None):
        self.source_file = source_file 
        if self.source_file is not None:
            # We are doing Task of Type1 (refer docstring)
            self.coln_pairs = coln_pairs 
            if destination_file is None:
                # destination file is not given so they want it to be inplace
                destination_file = source_file 
            self.destination_file = destination_file
            self._sanity_check()

            self.source_type = None 
            self.destination_type = None
            self.valid_extensions = ["csv", "xlsx"]
            self._get_type()
            
            self.data = None
            self.inplace = None
            self._load_data()

    def call_search(self, x, y=""):
        if type(y) == str and y.strip() != "":
            return y 
        # sanity check
        if  type(x) != str or x == "" or x is None:
            return self.alternate_text
        c = next(search(x, self.query, num_results=1, sleep_interval=self.sleep_interval))
        if c == "":
            c = self.alternate_text
        elif c == "STOP":
            # error happened 
            self.terminate = True
            return c
        if self.verbose > 0:
            print(x,"-->", c)
        return c
    
    def populate(self, query=None, replace_existing_links=False, lang="en", proxy=None, advanced=False, sleep_interval=20, timeout=5, alternate_text="Not Found", speedup=False, verbose=1):
        assert self.source_file is not None # sanity check
        # Everytime we call we don't want have same pattern of time interval, so we bring true randomness
        fix_random(true_random())

        self.terminate = False
        completed = False # if function finished normally by searching all rows: not by time limit or keyboard interrupt
        self._initialize(lang, proxy, advanced, sleep_interval, timeout, alternate_text, speedup, verbose) 
        self.query = query # Set now so that we don't set it for sanity check 

        if replace_existing_links:
            self.data.loc[:, self.coln_pairs[1]] = ""
        try:
            if speedup:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    self.data.loc[:, self.coln_pairs[1]] = list(executor.map(self.call_search, self.data.loc[:, self.coln_pairs[0]], self.data.loc[:, self.coln_pairs[1]]))
            else:
                # self.data[self.coln_pairs[1]] = self.data[self.coln_pairs[0]].apply(lambda x: self.call_search(x))    
                # Iterate through the rows of the DataFrame
                for index, value in self.data.loc[:, self.coln_pairs].iterrows():
                    x = value[self.coln_pairs[0]]
                    y = value[self.coln_pairs[1]]
                    res = self.call_search(x, y)
                    if self.terminate:
                        # Not to keep continuing if faced any server error
                        print("Wait for an hour!!!, or Connect to a different internet connection.")
                        # Also don't return, just do break to save atleast the data we collected
                        break
                    self.data.loc[index, self.coln_pairs[1]] = res 
                else:
                    completed= True

        except KeyboardInterrupt:
            # Code to handle the KeyboardInterrupt
            print("Execution interrupted by keyboard shortcut. Saving Results!!!")
        save_data(self.data, self.destination_file, self.destination_type)
        return completed

    def _initialize(self, lang, proxy, advanced, sleep_interval, timeout, alternate_text, speedup, verbose):
        self.lang = lang 
        self.proxy = proxy 
        self.advanced = advanced 
        self.sleep_interval = sleep_interval 
        self.timeout = timeout 
        self.alternate_text = alternate_text 
        self.speedup = speedup
        self.verbose = verbose 

    def query(self, queries, lang="en", proxy=None, advanced=False, sleep_interval=2, timeout=5, alternate_text="Not Found", speedup=False, verbose=1):
        self.query = None
        self._initialize(lang, proxy, advanced, sleep_interval, timeout, alternate_text, speedup, verbose)
        if type(queries) is str:
            # single query 
            return self.call_search(queries)
        elif isinstance(queries, list):
            if speedup:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    results = list(executor.map(self.call_search, queries))
            else:
                results = list(map(lambda x: self.call_search(x), queries)) 
            return results

    def _sanity_check(self):
        assert type(self.source_file) is str 
        assert type(self.destination_file) is str 
        assert self.source_file != ""
        assert self.destination_file != ""
        assert type(self.coln_pairs) is list 
        assert len(self.coln_pairs) in [1,2]

    def _get_type(self):
        self.source_type = self.source_file.split(".")[-1]
        self.destination_type = self.destination_file.split(".")[-1]
        assert self.source_type in self.valid_extensions and self.destination_type in self.valid_extensions

    def _load_data(self):
        self.data = load_data(self.source_file, self.source_type)
        if self.source_type == "csv":
            self.data = pd.read_csv(self.source_file)

        # need to assert, columns are present in data 
        assert self.coln_pairs[0] in self.data.columns.tolist()
        if len(self.coln_pairs) == 1:
            self.coln_pairs.append(f"{self.coln_pairs[0]}_link")
        if self.coln_pairs[1] not in self.data.columns.tolist():
            self.data.loc[:, self.coln_pairs[1]] = "" # initialize only if not present
        # don't initialize it
        #self.data.loc[:, self.coln_pairs[1]] = ""
        if self.source_file != self.destination_file:
            # we want to create new file 
            # drop rest of the columns 
            self.data = self.data[self.coln_pairs]

         
             



