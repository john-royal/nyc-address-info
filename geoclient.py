import requests


class GeoclientRequestHandler:
    FUNCTION_1B_URL = 'https://api.cityofnewyork.us/geoclient/v1/address.json'

    def __init__(self, app_id: str, app_key: str, request_properties: list):
        self.app_id = app_id
        self.app_key = app_key
        self.request_properties = request_properties

    def request_function_1b(self, address_number: str, street_name: str, borough: str):
        print('Requesting geoclient data for ' +
              str(address_number) + ' ' + street_name + ' ' + borough)

        response = requests.get(self.FUNCTION_1B_URL, { # pylint: disable=too-many-function-args
            'app_id': self.app_id,
            'app_key': self.app_key,
            'houseNumber': address_number,
            'street': street_name,
            'borough': borough
        })
        response.raise_for_status()
        response_json = response.json()

        return self._format_function_1b_result(response_json)

    def _format_function_1b_result(self, response_json: dict):
        result = {
            'ok': True,
            'message': None,
            'data': {}
        }

        # The 'address' property contains all the information we want.
        response_json = response_json['address']

        if response_json['geosupportReturnCode'] != '00':
            # A return code other than 00 indicates that there's a problem with
            # the address we requested information for. Since this is normal in
            # large data sets and we don't want an entire job to fail because of
            # one bad address, we're not going to raise an error. Instead, we'll
            # record what the issue is and keep going.

            result['ok'] = False
            result['message'] = 'GRC: ' + response_json['geosupportReturnCode']

            if 'message' in response_json:
                # Include the given message, plus the GRC we just retrieved.
                result['message'] = response_json['message'] + \
                    ' (' + result['message'] + ')'

        for property_name in self.request_properties:
            # Check for the property name before accessing it.
            # This prevents bad addresses from causing script-stopping errors.
            if property_name in response_json:
                result['data'][property_name] = response_json[property_name]
            else:
                result['data'][property_name] = None

        return result
