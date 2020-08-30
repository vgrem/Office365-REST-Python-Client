from generator.typeBuilder import TypeBuilder

from office365.runtime.odata.odata_v3_reader import ODataV3Reader
from office365.runtime.odata.odata_v4_reader import ODataV4Reader


def generate_files(model, options):
    for name in model.types:
        type_schema = model.types[name]
        builder = TypeBuilder(type_schema)
        if builder.build(options):
            builder.save()


def generate_sharepoint_model():
    generator_options = {
        'namespace': 'office365.sharepoint',
        'metadataPath': './metadata/SharePoint.xml',
        'outputPath': '/office365/sharepoint'
    }
    reader = ODataV3Reader(generator_options)
    model = reader.generate_model()
    generate_files(model, generator_options)


def generate_graph_model():
    options = {
        'namespace': 'office365',
        'metadataPath': './metadata/MicrosoftGraph.xml',
        'outputPath': '/office365',
        'entityTypeFile': 'office365/graph/base_item.py',
        'complexTypeFile': '../office365/runtime/client_value.py'
    }
    reader = ODataV4Reader(options)
    model = reader.generate_model()
    generate_files(model, options)


if __name__ == '__main__':
    generate_graph_model()
