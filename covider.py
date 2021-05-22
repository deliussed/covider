from typing import Iterable, Dict, Union, List
from json import dumps
from requests import get
from http import HTTPStatus




class Covider:



    StructureType = Dict[str, Union[dict, str]]
    FiltersType = Iterable[str]
    APIResponseType = Union[List[StructureType], str]

    def get_paginated_dataset(self,filters: FiltersType, structure: StructureType,
                              as_csv: bool = False) -> APIResponseType:
        """
        Extracts paginated data by requesting all of the pages
        and combining the results.

        Parameters
        ----------
        filters: Iterable[str]
            API filters. See the API documentations for additional
            information.

        structure: Dict[str, Union[dict, str]]
            Structure parameter. See the API documentations for
            additional information.

        as_csv: bool
            Return the data as CSV. [default: ``False``]

        Returns
        -------
        Union[List[StructureType], str]
            Comprehensive list of dictionaries containing all the data for
            the given ``filters`` and ``structure``.
        """


        endpoint = "https://api.coronavirus.data.gov.uk/v1/data"

        api_params = {
            "filters": str.join(";", filters),
            "structure": dumps(structure, separators=(",", ":")),
            "format": "json" if not as_csv else "csv"
        }

        data = list()

        page_number = 1

        while True:
            # Adding page number to query params
            api_params["page"] = page_number

            response = get(endpoint, params=api_params, timeout=10)

            if response.status_code >= HTTPStatus.BAD_REQUEST:
                raise RuntimeError(f'Request failed: {response.text}')
            elif response.status_code == HTTPStatus.NO_CONTENT:
                break

            if as_csv:
                csv_content = response.content.decode()

                # Removing CSV header (column names) where page
                # number is greater than 1.
                if page_number > 1:
                    data_lines = csv_content.split("\n")[1:]
                    csv_content = str.join("\n", data_lines)

                data.append(csv_content.strip())
                page_number += 1
                continue

            current_data = response.json()
            page_data: List[StructureType] = current_data['data']

            data.extend(page_data)

            # The "next" attribute in "pagination" will be `None`
            # when we reach the end.
            if current_data["pagination"]["next"] is None:
                break

            page_number += 1

        if not as_csv:
            return data

        # Concatenating CSV pages
        return str.join("\n", data)

    def get_results (self):

        days_counted   = 14
        infection_time = 7
        ignore_days    = 3

        app_results = {}
        eastleigh_query_filters = [
            f"areaType=ltla",
            f"areaName=Eastleigh"
        ]

        hampshire_query_filters = [
            f"areaType=utla",
            f"areaName=Hampshire"
        ]

        query_dict = {
            "Eastleigh":eastleigh_query_filters,
            "Hampshire":hampshire_query_filters
        }

        query_structure = {
            "date": "date",
            "name": "areaName",
            "code": "areaCode",
            "daily": "newCasesBySpecimenDate",
            "cumulative": "cumCasesBySpecimenDate"
        }

        output_strings = []
        forcast_strings = []

        for query_area in query_dict :
            json_data   = self.get_paginated_dataset(query_dict [query_area], query_structure)

            recent      = ignore_days
            less_recent = recent + infection_time
            day_count   = days_counted - infection_time
            r_total     = 0
            daily_total = 0
            r_date      = json_data[recent]["date"]

            area_dict   = {}

            area_dict['infection_time'] = infection_time
            area_dict['ignore_days'] = ignore_days
            area_dict['days_counted'] = days_counted

            app_results[query_area]=area_dict

            for i in range (day_count) :
                new_value = json_data[recent]["daily"]
                old_value = json_data[less_recent]["daily"]
                if i < infection_time :
                    daily_total += new_value
                if old_value == 0 :
                    old_value = 1
                r_value = new_value / old_value

                recent+=1
                less_recent +=1
                r_total += r_value


            r2_date = json_data[less_recent]["date"]

            daily_average = daily_total / infection_time
            final_r_value = r_total / day_count

            app_results[query_area]['daily_average'] = daily_average
            app_results[query_area]['r_value'] = final_r_value

            forcast_string = ("Average daily cases in "+query_area+" "+( "%s" %int(daily_average)))
            forcast_strings.append (forcast_string)
            forcast = daily_average


            for i in range (4) :
                forcast = forcast * final_r_value
            forcast_string = ("Forecast daily cases (static R) in four weeks in "+query_area+" "+("%s" %int(forcast) ) )
            forcast_strings.append (forcast_string)
            for i in range (8) :
                forcast = forcast * final_r_value
            forcast_string = ("Forecast daily cases (static R) in twelve weeks in "+query_area+" "+("%s" %int(forcast) ) )
            forcast_strings.append (forcast_string)
            output_string = "R value in " + query_area + " between " + r2_date + " and " + r_date + " is " + ( "%.1f" %final_r_value ) + " (1 d.p.)"
            output_strings.append (output_string)
    #    for o_string in output_strings :
    #        print ( o_string )
    #    for o_string in forcast_strings :
    #        print ( o_string )

        return app_results
