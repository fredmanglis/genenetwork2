from __future__ import print_function

import json
import reaper
import argparse

def init_loci(data):
    loci = []
    for dt in data:
        locus = reaper.Locus(name=str(dt["name"]), genotype=dt["genotype"],
                             chr=str(dt["chr"]), cM=dt["cM"], Mb=dt["Mb"])
        loci.append(locus)

    return loci

def init_chromosome(data):
    chromosomes = []
    for dt in data:
        chrm = reaper.Chromosome()
        chrm.name = str(dt["name"])
        chrm.loci = init_loci(dt["loci"])
        chromosomes.append(chrm)

    return chromosomes

def init_prgy(data):
    return map(str, data)

def init_genotype(args):
    data = None
    with open(args.filename, "r") as infile:
        data = infile.read()

    data = json.loads(data)
    genotype = reaper.Dataset()
    # genotype.name = str(data["name"])
    # genotype.mat = str(data["mat"])
    # genotype.pat = str(data["pat"])
    # genotype.type = str(data["type"])
    genotype.chromosome = init_chromosome(data["chromosome"])
    genotype.prgy = init_prgy(data["prgy"])
    # genotype.nprgy = len(data["prgy"])
    # genotype.dominance = data["dominance"]
    # genotype.Mb=data["Mb"]
    # genotype.interval = data["interval"]
    return genotype

def process_strains(args):
    args["strains"] = map(str, args["strains"])
    return args

def process_function_arguments(args):
    arguments = json.loads(args)
    arguments = dict((str(k),v) for k,v in arguments.items() if v is not None)
    arguments = process_strains(arguments)    
    return arguments

def process_data(args):
    genotype = init_genotype(args)
    arguments = process_function_arguments(args.arguments)
    print("THE ARGUMENTS ======>", arguments)

    result = getattr(genotype, args.action).__call__(**arguments)
    print(result)


if __name__ == '__main__':
    desc = """
py2_reaper_runner - This program runs QTLReaper, that only works in Python2 as
    an external process. This allows for it to be called from a Python3
    application for which there is no equivalent package.
"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("action", help="Select the action to take.",
                        choices=["bootstrap", "permutation", "regression"])
    parser.add_argument(
        "filename",
        help="File with JSON-encoded string of parsed genotype objects")
    parser.add_argument("arguments", help="JSON-encoded arguments to actions")
    process_data(parser.parse_args())
