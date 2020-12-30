'''
    part of flow network result viewer
'''

__author__ = ('Tom Streubel',) # alphabetical order of surnames
__credits__ = ('John Gerick',) # alphabetical order of surnames


'''
    imports
    =======
'''
import numpy as np
import yaml
import csv


def _retrieveDictTopoFromYaml(filePath):
    '''
        reading the yaml
    '''
    with open(filePath, mode = 'r') as netDictYaml:
        yamlTopo = yaml.load(netDictYaml, Loader = yaml.SafeLoader)

    return yamlTopo

def _retrieveResultsFromCsv(filePath):
    '''
        reading the csv
    '''

    Ts = []
    valueDicts = []
    currentDict = None

    with open(filePath, newline = '') as csvFile:
        resultreader = csv.DictReader(csvFile, delimiter = ';') #, quotechar = '|')

        for row in resultreader:
            ti = float(row['Time'])
            if not (ti in Ts):
                Ts.append(ti)
                valueDicts.append({})
                currentDict = valueDicts[-1]
            else:
                currentDict = valueDicts[Ts.index(ti)]

            id_obj = row['Object']
            if not (id_obj in currentDict):
                currentDict[id_obj] = {}

            currentDict[id_obj][row['Parameter']] = {'Value' : float(row['Value']), 'Unit' : row['Unit']}

    return Ts, valueDicts


def create_yaml_Files(NetDictYaml_path, resultCSV_path, resultMeta_path, outPath, export = False, **options):
    if not (resultMeta_path is None):
        with open(resultMeta_path, mode = 'r') as result_meta:
            meta_dict = yaml.load(result_meta, Loader = yaml.SafeLoader)

    topoPath = NetDictYaml_path
    showName_innode = options.get('innode_labels', False)
    showName_bound = options.get('boundary_labels', True)

    resultPath = resultCSV_path
    showName_pipe = options.get('pipe_labels', False)
    showName_resistor = options.get('resistor_Labels', False)
    showName_vlv = options.get('valve_labels', False)
    showName_compressor = options.get('compressor_labels', True)
    showName_cv = options.get('controlValve_labels', True)
    showName_ch = options.get('checkValve_labels', True)

    plot_activity_bars = options.get('plot_activity_bars', False)

    simName = options.get('outputFile_name', 'generic')


    showNameArcDict = {'pipe'         : showName_pipe,
                       'resistor'     : showName_resistor,
                       'valve'        : showName_vlv,
                       'controlValve' : showName_cv,
                       'compressor'   : showName_compressor,
                       'checkValve'   : showName_ch}

    Ts, valueDicts = _retrieveResultsFromCsv(resultPath)

    nodes4yaml = []
    nodes4yaml_dict = {}
    elements4yaml = []
    elements4yaml_dict = {}

    dictTopo = _retrieveDictTopoFromYaml(topoPath)

    arcsPerType = dictTopo['arcsPerType']
    nodesPerType = dictTopo['nodesPerType']

    '''
        create yaml for nodes for result viewer
    '''
    for nodeTypeKey_yaml, nodesOfType_yaml in nodesPerType.items():
        for node_yaml in nodesOfType_yaml:
            node4yaml = {'id': node_yaml['id']['value'],
                         'x': node_yaml['x']['value'], 'y': node_yaml['y']['value'],
                         'showName': showName_innode,
                         'valuesPressure' : []}
            if nodeTypeKey_yaml in ['source', 'sink']:
                node4yaml['showName'] = showName_bound

            nodes4yaml.append(node4yaml)
            nodes4yaml_dict[node4yaml['id']] = node4yaml

    '''
        create yaml for elements for result viewer
    '''
    for arcTypeKey_yaml, arcsOfType_yaml in arcsPerType.items():
        for arc_yaml in arcsOfType_yaml:
            element_id = arc_yaml['id']['value']

            element4yaml = {'id': element_id + " ({})".format(arcTypeKey_yaml),
                            'von': arc_yaml['from']['value'], 'nach': arc_yaml['to']['value'],
                            'showName': showNameArcDict[arcTypeKey_yaml],
                            'diameter': arc_yaml.get('diameter', {'value' : 1.0e-3})['value']*1.0e3,
                            'length': arc_yaml.get('length', {'value': 1.0e3})['value']*1.0e-3,
                            'valuesPressure' : [],
                            'valuesFlow' : []}

            if not (resultMeta_path is None):
                if element_id in meta_dict['valve']:
                    if plot_activity_bars:
                        element4yaml['opening-states'] = meta_dict['valve'][element_id]['opening-states']
                elif element_id in meta_dict['compressorStation']:
                    if plot_activity_bars:
                        element4yaml['opening-states'] = meta_dict['compressorStation'][element_id]['opening-states']
                        element4yaml['bypass-states'] = meta_dict['compressorStation'][element_id]['bypass-states']
                    element4yaml['q_target_q'] = meta_dict['compressorStation'][element_id]['q_target_q']
                    element4yaml['p_target_lower_pL'] = meta_dict['compressorStation'][element_id]['p_target_lower_pL']
                    element4yaml['p_target_upper_pR'] = meta_dict['compressorStation'][element_id]['p_target_upper_pR']
                elif element_id in meta_dict['controlValve']:
                    if plot_activity_bars:
                        element4yaml['opening-states'] = meta_dict['controlValve'][element_id]['opening-states']
                        element4yaml['bypass-states'] = meta_dict['controlValve'][element_id]['bypass-states']
                    element4yaml['q_target_q'] = meta_dict['controlValve'][element_id]['q_target_q']
                    element4yaml['p_target_lower_pL'] = meta_dict['controlValve'][element_id]['p_target_lower_pL']
                    element4yaml['p_target_upper_pR'] = meta_dict['controlValve'][element_id]['p_target_upper_pR']
                    element4yaml['p_target_upper_pL'] = meta_dict['controlValve'][element_id]['p_target_upper_pL']
                    element4yaml['p_target_lower_pR'] = meta_dict['controlValve'][element_id]['p_target_lower_pR']

            elements4yaml.append(element4yaml)
            # elements4yaml_dict[element4yaml['id']] = element4yaml
            elements4yaml_dict[element_id] = element4yaml

    '''
        filling values into dict structures
    '''
    for ti, csv_objects in zip(Ts, valueDicts):
        for obj_id, params in csv_objects.items():
            if 'P' in params:
                nodes4yaml_dict[obj_id]['valuesPressure'].append(params['P']['Value'])

    for idx, (ti, csv_objects) in enumerate(zip(Ts, valueDicts)):
        for obj_id, params in csv_objects.items():
            if ('ML' in params) or ('M' in params):
                currentElement = elements4yaml_dict[obj_id]
                fromNode = nodes4yaml_dict[currentElement['von']]['valuesPressure']
                toNode   = nodes4yaml_dict[currentElement['nach']]['valuesPressure']
                currentElement['valuesPressure'].append([fromNode[idx], toNode[idx]])

                if 'ML' in params:
                    currentElement['valuesFlow'].append([params['ML']['Value'], params['MR']['Value']])
                else:
                    currentElement['valuesFlow'].append([params['M']['Value'], params['M']['Value']])

    units4yaml = {"pressure": "bar", "flow": "kg_per_s"}

    if export:
        for ending, data in zip(('viewer.nodes.yaml', 'viewer.elements.yaml', 'viewer.times4Results.yaml'),
                                (nodes4yaml, elements4yaml, Ts)):
            with open(outPath + '{}.{}'.format(simName, ending), 'w') as outfile:
                # json.dump(data, outfile, indent = 2)
                yaml.dump(data, outfile, indent = 4, default_flow_style = None)

        with open(outPath + '{}.{}'.format(simName, "viewer.units.yaml"), 'w') as outfile:
            yaml.dump(units4yaml, outfile, indent = 4, default_flow_style = None)

    return Ts, nodes4yaml, elements4yaml, units4yaml


if __name__ == '__main__':
    # create_json_Files('distr_20.netDict.yaml', 'result.csv')

    # showName_innode = options.get('innode_labels', False)
    # showName_bound = options.get('boundary_labels', True)
    #
    # showName_pipe = options.get('pipe_labels', False)
    # showName_resistor = options.get('resistor_Labels', False)
    # showName_vlv = options.get('valve_labels', False)
    # showName_cStation = options.get('compressor_labels', True)
    # showName_cv = options.get('controlValve_labels', True)
    #
    # simName = options.get('outputFile_name', 'generic')

    print('finished!')
