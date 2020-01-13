from office365.runtime.odata.odata_v4_reader import ODataV4Reader

if __name__ == '__main__':
    generator_options = {
        'namespace': '',
        'inputPath': './metadata/MicrosoftGraph15122019.xml',
        'outputPath': ''
    }
    reader = ODataV4Reader(generator_options)
    model = reader.generate_model()
    print(model)
