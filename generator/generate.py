from office365.runtime.odata.odata_v3_reader import ODataV3Reader
from office365.runtime.odata.odata_v4_reader import ODataV4Reader

if __name__ == '__main__':
    generator_options = {
        'namespace': 'office365',
        'inputPath': './metadata/MicrosoftGraph15122019.xml',
        'outputPath': '/office365'
    }
    reader = ODataV4Reader(generator_options)
    model = reader.generate_model()
    print(model)

    generator_options_sharepoint = {
        'namespace': 'office365.sharepoint',
        'inputPath': './metadata/SharePoint.xml',
        'outputPath': '/office365/sharepoint'
    }
    reader = ODataV3Reader(generator_options_sharepoint)
    model = reader.generate_model()
    print(model)
