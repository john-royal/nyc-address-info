import pandas as pd


class _SpreadsheetRow:
    def __init__(self, index: int, data: pd.Series, columns: list, dataframe: pd.DataFrame):
        self.index = index
        self.data = data
        self.columns = columns
        self.dataframe = dataframe

    def get(self, property_name):
        index = self.columns.index(property_name)
        return self.data[index]

    def set(self, property_name, new_value):
        self.dataframe.at[self.index, property_name] = new_value

    def set_multiple(self, property_value_dict):
        for name, value in property_value_dict.items():
            self.dataframe.at[self.index, name] = value


class LocationsSpreadsheet:
    columns = [
        'address_number',
        'street_name',
        'unit',
        'borough'
    ]
    dataframe = None
    total_rows = None

    def __init__(self, location_files: list, save_file: str, save_sheet: str):
        # Load data from the given spreadsheets.
        for location_list in location_files:
            self.add_locations_from_file(
                file_name=location_list['file'],
                sheet_name=location_list['sheet']
            )
        # Normalize the loaded data.
        self.normalize_data()
        # Record where we're saving output to.
        self.save_file = save_file
        self.save_sheet = save_sheet

    def add_locations_from_file(self, file_name: str, sheet_name: str):
        print('Loading locations from ' + file_name + ' ' + sheet_name)
        file = pd.read_excel(file_name, sheet_name, 0, self.columns)
        # Determine whether to append this file to an existing dataframe.
        # Panda throws an error if you compare to a dataframe, so we're
        # comparing to the number of rows instead.
        if self.total_rows == None:
            self.dataframe = file
        else:
            self.dataframe = pd.concat([
                self.dataframe,
                file
            ])
        self.total_rows = self.dataframe.count()[0]

    def normalize_data(self):
        self.dataframe = self.dataframe.drop_duplicates().reset_index(drop=True).sort_index()

    def insert_column(self, column_name):
        self.columns.append(column_name)
        index = self.columns.index(column_name)
        self.dataframe.insert(index, column_name, '')

    def rows(self):
        for i, data in self.dataframe.iterrows():
            yield _SpreadsheetRow(i, data, self.columns, self.dataframe)

    def save(self):
        file = self.save_file
        sheet = self.save_sheet
        print('Saving data to ' + file + ' ' + sheet)
        self.dataframe.to_excel(file, sheet)
