from generator.builders.type_builder import TypeBuilder

from office365.runtime.odata.odata_v3_reader import ODataV3Reader
from office365.runtime.odata.odata_v4_reader import ODataV4Reader


def generate_files(model, options):
    for name in model.types:
        type_schema = model.types[name]
        builder = TypeBuilder(options)
        result = builder.build(type_schema)
        if result["status"] == "created":
            builder.save(result)


def generate_sharepoint_model():
    generator_options = {
        'namespace': 'office365.sharepoint',
        'metadataPath': './metadata/SharePoint.xml',
        'outputPath': '/office365/sharepoint',
        'templatePath': '/generator/templates',
    }
    reader = ODataV3Reader(generator_options)
    model = reader.generate_model()
    generate_files(model, generator_options)


def generate_graph_model():
    options = {
        'namespace': 'office365',
        'metadataPath': './metadata/MicrosoftGraph.xml',
        'outputPath': '../office365',
        'templatePath': '../generator/templates',
    }
    reader = ODataV4Reader(options)
    model = reader.generate_model()
    generate_files(model, options)


if __name__ == '__main__':
    generate_graph_model()
