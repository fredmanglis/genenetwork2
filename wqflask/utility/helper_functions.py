

from base.trait import GeneralTrait
from base import data_set
from base.species import TheSpecies

from wqflask import user_manager, app

from flask import Flask, g

import logging
logger = logging.getLogger(__name__ )


def get_species_dataset_trait(self, start_vars):
    #assert type(read_genotype) == type(bool()), "Expecting boolean value for read_genotype"
    self.dataset = data_set.create_dataset(start_vars['dataset'])
    logger.debug("After creating dataset")
    self.species = TheSpecies(dataset=self.dataset)
    logger.debug("After creating species")
    self.this_trait = GeneralTrait(dataset=self.dataset,
                                   name=start_vars['trait_id'],
                                   cellid=None,
                                   get_qtl_info=True)
    logger.debug("After creating trait")

    #if read_genotype:
    #self.dataset.group.read_genotype_file()
    #self.genotype = self.dataset.group.genotype


def get_trait_db_obs(self, trait_db_list):
    if isinstance(trait_db_list, str):
        trait_db_list = trait_db_list.split(",")

    self.trait_list = []
    for trait in trait_db_list:
        data, _separator, hmac = trait.rpartition(':')
        data = data.strip()
        assert hmac==user_manager.actual_hmac_creation(data, app.config['SECRET_HMAC_CODE']), "Data tampering?"
        trait_name, dataset_name = data.split(":")
        dataset_ob = data_set.create_dataset(dataset_name)
        trait_ob = GeneralTrait(dataset=dataset_ob,
                               name=trait_name,
                               cellid=None)
        self.trait_list.append((trait_ob, dataset_ob))

def get_species_groups():

    species_query = "SELECT SpeciesId, MenuName FROM Species"
    species_ids_and_names = g.db.execute(species_query).fetchall()

    species_and_groups = []
    for species_id, species_name in species_ids_and_names:
        this_species_groups = {}
        this_species_groups['species'] = species_name
        groups_query = "SELECT InbredSetName FROM InbredSet WHERE SpeciesId = %s" % (species_id)
        groups = [group[0] for group in g.db.execute(groups_query).fetchall()]

        this_species_groups['groups'] = groups
        species_and_groups.append(this_species_groups)

    return species_and_groups
