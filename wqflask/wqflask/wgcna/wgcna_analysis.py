# WGCNA analysis for GN2
# Author / Maintainer: Danny Arends <Danny.Arends@gmail.com>
import sys
from numpy import *
import scipy as sp                            # SciPy
import rpy2.robjects as ro                    # R Objects
import rpy2.rinterface as ri

from base.webqtlConfig import GENERATED_IMAGE_DIR
from utility import webqtlUtil                # Random number for the image

import base64
import array

from utility import helper_functions

from rpy2.robjects.packages import importr
utils = importr("utils")

## Get pointers to some common R functions
r_library       = ro.r["library"]             # Map the library function
r_options       = ro.r["options"]             # Map the options function
r_read_csv      = ro.r["read.csv"]            # Map the read.csv function
r_dim           = ro.r["dim"]                 # Map the dim function
r_c             = ro.r["c"]                   # Map the c function
r_cat           = ro.r["cat"]                 # Map the cat function
r_paste         = ro.r["paste"]               # Map the paste function
r_unlist        = ro.r["unlist"]              # Map the unlist function
r_unique        = ro.r["unique"]              # Map the unique function
r_length        = ro.r["length"]              # Map the length function
r_unlist        = ro.r["unlist"]              # Map the unlist function
r_list          = ro.r.list                   # Map the list function
r_matrix        = ro.r.matrix                 # Map the matrix function
r_seq           = ro.r["seq"]                 # Map the seq function
r_table         = ro.r["table"]               # Map the table function
r_names         = ro.r["names"]               # Map the names function
r_sink          = ro.r["sink"]                # Map the sink function
r_is_NA         = ro.r["is.na"]               # Map the is.na function
r_file          = ro.r["file"]                # Map the file function
r_png           = ro.r["png"]                 # Map the png function for plotting
r_dev_off       = ro.r["dev.off"]             # Map the dev.off function

class WGCNA(object):
    def __init__(self):
        print("Initialization of WGCNA")
        #log = r_file("/tmp/genenetwork_wcgna.log", open = "wt")
        #r_sink(log)                                  # Uncomment the r_sink() commands to log output from stdout/stderr to a file
        #r_sink(log, type = "message")
        r_library("WGCNA")                            # Load WGCNA - Should only be done once, since it is quite expensive
        r_options(stringsAsFactors = False)
        print("Initialization of WGCNA done, package loaded in R session")
        self.r_enableWGCNAThreads    = ro.r["enableWGCNAThreads"]        # Map the enableWGCNAThreads function
        self.r_pickSoftThreshold     = ro.r["pickSoftThreshold"]         # Map the pickSoftThreshold function
        self.r_blockwiseModules      = ro.r["blockwiseModules"]          # Map the blockwiseModules function
        self.r_labels2colors         = ro.r["labels2colors"]             # Map the labels2colors function
        self.r_plotDendroAndColors   = ro.r["plotDendroAndColors"]       # Map the plotDendroAndColors function
        print("Obtained pointers to WGCNA functions")

    def run_analysis(self, requestform):
        print("Starting WGCNA analysis on dataset")
        self.r_enableWGCNAThreads()                                      # Enable multi threading
        self.trait_db_list = [trait.strip() for trait in requestform['trait_list'].split(',')]
        print(("Retrieved phenotype data from database", requestform['trait_list']))
        helper_functions.get_trait_db_obs(self, self.trait_db_list)

        self.input = {}           # self.input contains the phenotype values we need to send to R
        strains = []              # All the strains we have data for (contains duplicates)
        traits  = []              # All the traits we have data for (should not contain duplicates)
        for trait in self.trait_list:
            traits.append(trait[0].name)
            self.input[trait[0].name] = {}
            for strain in trait[0].data:
                strains.append(strain)
                self.input[trait[0].name][strain]  = trait[0].data[strain].value

        # Transfer the load data from python to R
        uStrainsR = r_unique(ro.Vector(strains))    # Unique strains in R vector
        uTraitsR = r_unique(ro.Vector(traits))      # Unique traits in R vector

        r_cat("The number of unique strains:", r_length(uStrainsR), "\n")
        r_cat("The number of unique traits:", r_length(uTraitsR), "\n")

        # rM is the datamatrix holding all the data in R /rows = strains columns = traits
        rM = ro.r.matrix(ri.NA_Real, nrow=r_length(uStrainsR), ncol=r_length(uTraitsR), dimnames = r_list(uStrainsR, uTraitsR))
        for t in uTraitsR:
            trait = t[0]                  # R uses vectors every single element is a vector
            for s in uStrainsR:
                strain = s[0]             # R uses vectors every single element is a vector
                #DEBUG: print(trait, strain, " in python: ", self.input[trait].get(strain), "in R:", rM.rx(strain,trait)[0])
                rM.rx[strain, trait] = self.input[trait].get(strain)  # Update the matrix location
                sys.stdout.flush()

        self.results = {}
        self.results['nphe'] = r_length(uTraitsR)[0]          # Number of phenotypes/traits
        self.results['nstr'] = r_length(uStrainsR)[0]         # Number of strains
        self.results['phenotypes'] = uTraitsR                 # Traits used
        self.results['strains'] = uStrainsR                   # Strains used in the analysis
        self.results['requestform'] = requestform             # Store the user specified parameters for the output page

        # Calculate soft threshold if the user specified the SoftThreshold variable
        if requestform.get('SoftThresholds') is not None:
          powers = [int(threshold.strip()) for threshold in requestform['SoftThresholds'].rstrip().split(",")]
          rpow = r_unlist(r_c(powers))
          print("SoftThresholds: {} == {}".format(powers, rpow))
          self.sft    = self.r_pickSoftThreshold(rM, powerVector = rpow, verbose = 5)

          print("PowerEstimate: {}".format(self.sft[0]))
          self.results['PowerEstimate'] = self.sft[0]
          if self.sft[0][0] is ri.NA_Integer:
            print("No power is suitable for the analysis, just use 1")
            self.results['Power'] = 1                         # No power could be estimated
          else:
            self.results['Power'] = self.sft[0][0]            # Use the estimated power
        else:
          # The user clicked a button, so no soft threshold selection
          self.results['Power'] = requestform.get('Power')    # Use the power value the user gives

        # Create the block wise modules using WGCNA
        network = self.r_blockwiseModules(rM, power = self.results['Power'], TOMType = requestform['TOMtype'], minModuleSize = requestform['MinModuleSize'], verbose = 3)

        # Save the network for the GUI
        self.results['network'] = network

        # How many modules and how many gene per module ?
        print("WGCNA found {} modules".format(r_table(network[1])))
        self.results['nmod'] = r_length(r_table(network[1]))[0]

        # The iconic WCGNA plot of the modules in the hanging tree
        self.results['imgurl'] = webqtlUtil.genRandStr("WGCNAoutput_") + ".png"
        self.results['imgloc'] = GENERATED_IMAGE_DIR + self.results['imgurl']
        r_png(self.results['imgloc'], width=1000, height=600, type='cairo-png')
        mergedColors = self.r_labels2colors(network[1])
        self.r_plotDendroAndColors(network[5][0], mergedColors, "Module colors", dendroLabels = False, hang = 0.03, addGuide = True, guideHang = 0.05)
        r_dev_off()
        sys.stdout.flush()

    def render_image(self, results):
        print(("pre-loading imgage results:", self.results['imgloc']))
        imgfile = open(self.results['imgloc'], 'rb')
        imgdata = imgfile.read()
        imgB64 = imgdata.encode("base64")
        bytesarray = array.array('B', imgB64)
        self.results['imgdata'] = bytesarray

    def process_results(self, results):
        print("Processing WGCNA output")
        template_vars = {}
        template_vars["input"] = self.input
        template_vars["powers"] = self.sft[1:]                      # Results from the soft threshold analysis
        template_vars["results"] = self.results
        self.render_image(results)
        sys.stdout.flush()
        #r_sink(type = "message")                                   # This restores R output to the stdout/stderr
        #r_sink()                                                   # We should end the Rpy session more or less
        return(dict(template_vars))

