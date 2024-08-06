# 490011796N rushett lane
# 490011796S


# 490014149S walpole road south

import requests
import json
import datetime


from departure_service import (
    Departure,
    DepartureStatus,
    DeparturesInfo,
    TransitType,
    DepartureService,
)


class TflStopPointService(DepartureService):
    def __init__(self, naptan: str):
        self.naptan = naptan

    def __str__(self):
        return f"TflStopPointService({self.naptan})"

    def get_board_sync(self) -> DeparturesInfo:
        try:
            response = requests.get(
                f"https://api.tfl.gov.uk/StopPoint/{self.naptan}/Arrivals"
            )
            data = json.loads(response.content)
            deps = [self.parse_departure(d) for d in data]
            deps = [d for d in deps if d is not None]

            deps.sort(key=lambda d: d.arrival_time)

            stop_point_info = requests.get(
                f"https://api.tfl.gov.uk/StopPoint/{self.naptan}"
            )
            stop_point_data = json.loads(stop_point_info.content)

            return DeparturesInfo(TransitType.BUS, stop_point_data["commonName"], deps)
        except Exception as e:
            return DeparturesInfo(TransitType.BUS, self.naptan, [], str(e))

    def parse_departure(self, dep) -> Departure:
        line = dep["lineName"]
        dest = dep["destinationName"]

        arrival_ts = dep["expectedArrival"]
        arrival = datetime.datetime.fromisoformat(arrival_ts)

        arrival_diff = arrival - datetime.datetime.now(datetime.UTC)

        if arrival_diff.total_seconds() < 0:
            return None

        minutes = round(arrival_diff.seconds / 60)
        to = f"{line} to {dest}"

        if minutes == 0:
            etd = "Due"
        else:
            etd = f"{minutes} min"

        return Departure(to, None, etd, DepartureStatus.ON_TIME, arrival_time=arrival)


if __name__ == "__main__":
    b = TflStopPointService("490014149S")
    d = b.get_board_sync()
    print(d)
