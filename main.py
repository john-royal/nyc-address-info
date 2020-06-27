from dotenv import load_dotenv, find_dotenv
from config import ConfigManager
from geoclient import GeoclientRequestHandler
from spreadsheet import LocationsSpreadsheet


class FindNYCAddressInfo:
    def __init__(self, config: ConfigManager):
        # Set up locations spreadsheet
        locations_spreadsheet = LocationsSpreadsheet(
            location_files=config.inputs,
            save_file=config.output['file'],
            save_sheet=config.output['sheet']
        )
        # Insert empty columns for each property we're going to add
        for column_name in config.geoclient_request_properties:
            locations_spreadsheet.insert_column(column_name)
        locations_spreadsheet.insert_column('note')
        self.locations_spreadsheet = locations_spreadsheet

        # Set up Geoclient request handler
        self.geoclient = GeoclientRequestHandler(
            app_id=config.geoclient_app_id,
            app_key=config.geoclient_app_key,
            request_properties=config.geoclient_request_properties
        )

    def run(self):
        for location in self.locations_spreadsheet.rows():
            self._handle_location(location)
            self._save_spreadsheet_if_checkpoint(location.index)

    def _handle_location(self, location):
        # Get Geoclient data for this row
        response = self.geoclient.request_function_1b(
            address_number=location.get('address_number'),
            street_name=location.get('street_name'),
            borough=location.get('borough')
        )
        # Write data and error message if applicable
        location.set_multiple(response['data'])
        if not response['ok']:
            location.set('note', response['message'])

    def _save_spreadsheet_if_checkpoint(self, location_index):
        # Save and log progress every 10 rows and on the last row
        number = location_index + 1
        total = self.locations_spreadsheet.total_rows
        checkpoint = number % 10 == 0 or number == total
        if checkpoint:
            self.locations_spreadsheet.save()
            print('Finished ' + str(number) +
                  ' of ' + str(total) + ' locations')
            print()


def main():
    print('Find NYC Address Info')
    print()  # Empty lines used to separate log into related blocks

    # Set everything up
    load_dotenv(find_dotenv())
    config = ConfigManager(file_name='config.yml')
    find_nyc_address_info = FindNYCAddressInfo(config)
    print()

    find_nyc_address_info.run()
    print('Exiting')


if __name__ == '__main__':
    main()
