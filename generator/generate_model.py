
from generator import load_settings
from generator.builders.type_builder import TypeBuilder
from office365.runtime.odata.v3.metadata_reader import ODataV3Reader
from office365.runtime.odata.v4.metadata_reader import ODataV4Reader


def generate_files(model, options):
    # type: (ODataModel, dict) -> None
    for name in model.types:
        type_schema = model.types[name]
        builder = TypeBuilder(type_schema, options)
        builder.build()
        if builder.status == "created":
            builder.save()


def generate_sharepoint_model(settings):
    # type: (ConfigParser) -> None
    reader = ODataV3Reader(settings.get("sharepoint", "metadataPath"))
    reader.format_file()
    model = reader.generate_model()
    generate_files(model, dict(settings.items("sharepoint")))


def generate_graph_model(settings):
    # type: (ConfigParser) -> None
    reader = ODataV4Reader(settings.get("microsoftgraph", "metadataPath"))
    model = reader.generate_model()
    generate_files(model, dict(settings.items("microsoftgraph")))


if __name__ == "__main__":
    generator_settings = load_settings()
    # generate_graph_model(settings)
    generate_sharepoint_model(generator_settings)
