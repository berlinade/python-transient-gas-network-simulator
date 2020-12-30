'''
    reader for configuration yaml of the simulator itself
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.resources.auxiliary import ConfigDescriptionError

import yaml


class configuration(object):

    def __init__(self, path_config_yaml : str):
        if not (path_config_yaml[-23:] == '.config.simulation.yaml'):
            raise ConfigDescriptionError("config file must end on '.config.simulation.yaml'!")

        with open(path_config_yaml, mode = 'r') as config_yaml:
            self.raw = yaml.load(config_yaml, Loader = yaml.SafeLoader)

        self.name_of_instance = self.raw['name_of_instance']

        self.file_path_in = self.raw['file_path_in']
        self.file_path_out = self.raw['file_path_out']

        self.path_in_net_yaml = self.file_path_in + self.name_of_instance + '.net.yaml'
        self.path_in_inic_csv = self.file_path_in + self.name_of_instance + '.inic.csv'
        self.path_in_scene_csv = self.file_path_in + self.name_of_instance + '.recom.csv'

        self.path_out_results_csv  = self.file_path_out + self.name_of_instance + '.result.csv'

        write_additional_csvs = self.raw.get('write_additional_result_csv', {})
        self.path_out_results_pressures_csv  = self.file_path_out + self.name_of_instance + '.pressures_only.result.csv'
        self.write_pressures = write_additional_csvs.get('pressures_only', False)
        self.path_out_results_inner_flows_csv  = self.file_path_out + self.name_of_instance + '.inner_flows_only.result.csv'
        self.write_inner_flows = write_additional_csvs.get('inner_flows_only', False)
        self.path_out_results_boundary_flows_csv  = self.file_path_out + self.name_of_instance + '.boundary_flows_only.result.csv'
        self.write_boundary_flows = write_additional_csvs.get('boundary_flows_only', False)

        if self.raw.get('generate_results_meta', True):
            self.path_out_results_meta_yaml = self.file_path_out + self.name_of_instance + '.result.meta.yaml'
        else:
            self.path_out_results_meta_yaml = None

        if not ('file_path_dump' in self.raw):
            self.raw['file_path_dump'] = self.file_path_out

        if self.raw.get('dump_files', True):
            self.file_path_dump = self.raw['file_path_dump']
        else:
            self.file_path_dump = None

        self.write_left_right_flows = (not self.raw.get('write_mid_flows_for_pipes', False))

    @property
    def name_net_yaml(self):
        return self.name_of_instance + '.net.yaml'

    @property
    def delimiter(self): # csv delimiter
        return ';'

    @property
    def Hmin(self):
        return self.raw['Hmin']

    @property
    def rel_tol(self):
        return self.raw['rel_tol']

    @property
    def root_methods(self):
        return self.raw['root_methods']
