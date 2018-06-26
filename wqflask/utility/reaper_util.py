import json
from . import external

def regression(genotype, strains, trait, variance=None, control=None):
    args = {"strains": strains, "trait":trait, "variance":variance,
            "control":control}
    result = run_process("regression", genotype, args)
    return results

def permutation(genotype, strains, trait, variance=None, nperm=10, thresh=None, topN=10):
    args = {"strains": strains, "trait":trait, "variance":variance,
            "nperm":nperm, "thresh":thresh, "topN":topN}
    result = run_process("regression", genotype, args)
    return results

def bootstrap(genotype, strains, trait, variance=None, control=None, nboot=10):
    args = {"strains": strains, "trait":trait, "variance":variance,
            "control":control, "nboot":nboot}
    result = external.run_with_python2("bootstrap", genotype, args)
    return result

def generate_json(genotype):
    return json.dumps(generate_geno_dict(genotype))

def generate_geno_dict(genotype):
    chr_dict = [generate_chromosome_dict(chrm) for chrm in genotype.chromosome]
    dt_dict = genotype.__dict__
    dt_dict["chromosome"] = chr_dict
    return dt_dict

def generate_chromosome_dict(chromosome):
    loci_dict = [loc.__dict__ for loc in chromosome.loci]
    chrm_dict = chromosome.__dict__
    chrm_dict["loci"] = loci_dict
    return chrm_dict

def run_process(action, geno, extra_args):
    import random
    import string
    rand_str = ''.join(random.choice(string.ascii_letters + string.digits) for
                       _ in range(10))
    filename = "/tmp/geno_data_{}.json".format(rand_str)
    with open(filename, "w") as outfile:
        outfile.write("{}".format(generate_json(geno)))

    args = ["wqflask.utility.py2_reaper_runner", action, filename,
            "'{}'".format(json.dumps(extra_args))]
    result = external.run_with_python2(args)
    return result
