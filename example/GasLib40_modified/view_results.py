from example.GasLib40_modified.main import configPath
from simulator.readerWriter.read_config_yaml import configuration

from Viewer.converters.resultCSV_2_yaml import create_yaml_Files
from Viewer.ResultViewer import viewResults


config = configuration(path_config_yaml = configPath)

'''
    convert result to json for viewer
'''
options = {'innode_labels' : False,
           'boundary_labels' : True,
           'pipe_labels' : False,
           'resistor_Labels' : False,
           'valve_labels' : False,
           'compressor_labels' : True,
           'controlValve_labels' : True,
           'outputFile_name' : config.name_of_instance,
           'plot_activity_bars' : True}

# see simulated result
viewResults(*create_yaml_Files(config.path_in_net_yaml,
                               config.path_out_results_csv, config.path_out_results_meta_yaml,
                               config.file_path_out, **options),
            pathRVConfig = config.file_path_in + "g40.RVConfig.yaml")

# see generated result
# viewResults(*create_json_Files(config.path_in_net_yaml, config.file_path_in + "generic.result.csv", config.file_path_out, **options))
