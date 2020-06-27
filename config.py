import os
import yaml

class ConfigManager:
    def __init__(self, file_name):
        # Load inputs and outputs from file
        print('Loading configuration from ' + file_name)
        config = self.load_from_yaml_file(file_name)
        self.inputs = config['inputs']
        self.output = config['output']
        self.geoclient_request_properties = config['geoclient_request_properties']

        # Load API credentials from env
        print('Loading API credentials from env')
        self.geoclient_app_id = os.getenv('GEOCLIENT_APP_ID')
        self.geoclient_app_key = os.getenv('GEOCLIENT_APP_KEY')

        self.validate()

    def load_from_yaml_file(self, file_name):
        file_contents = open(file_name)
        return yaml.load(file_contents, Loader=yaml.FullLoader)

    def validate(self):
        # Inputs aren't validated here because if they're invalid,
        # Panda will raise an error and the script will not run.
        
        if not (self.output['file'] and self.output['sheet']):
            raise AttributeError('Missing output file and/or sheet')
        if not (self.geoclient_app_id and self.geoclient_app_key):
            raise AttributeError('Missing app_id and/or app_key')

        # Use geoclient-properties.yml to validate the requested property names.
        allowed_properties = self.load_from_yaml_file('geoclient-properties.yml')
        for property_name in self.geoclient_request_properties:
            if property_name not in allowed_properties:
                raise AttributeError('Unrecognized geoclient request property: ' + property_name)