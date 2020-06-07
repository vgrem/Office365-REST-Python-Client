import ast

from office365.runtime.odata.odata_v3_reader import ODataV3Reader
from office365.runtime.odata.odata_v4_reader import ODataV4Reader


def generate_files(model):
    for name in model.types:
        generate_type_file(model.types[name])


def generate_type_file(type_schema):
    if type_schema['state'] == 'attached':
        tree = ast.parse(open(type_schema['file']).read())
        print(type_schema['file'])


def generate_sharepoint_model():
    generator_options = {
        'namespace': 'office365.sharepoint',
        'inputPath': './metadata/SharePoint.xml',
        'outputPath': '/office365/sharepoint'
    }
    reader = ODataV3Reader(generator_options)
    model = reader.generate_model()
    generate_files(model)


def generate_graph_model():
    generator_options = {
        'namespace': 'office365',
        'inputPath': './metadata/MicrosoftGraph.xml',
        'outputPath': '/office365'
    }
    reader = ODataV4Reader(generator_options)
    model = reader.generate_model()
    generate_files(model)


if __name__ == '__main__':
    generate_graph_model()
