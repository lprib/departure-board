from zeep import Client, Settings, xsd
from zeep.plugins import HistoryPlugin

# import PySide6.QtAsyncio as QtAsyncio
import asyncio

from departure_service import (
    Departure,
    DepartureStatus,
    DeparturesInfo,
    TransitType,
    DepartureService,
)

from config import Config

# https://lite.realtime.nationalrail.co.uk/OpenLDBWS/


class RailDepartureService(DepartureService):
    WSDL = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2021-11-01"

    def __init__(self, api_token: str, crs: str, operator_filter: str | None = None):
        self.api_token = api_token
        self.crs = crs
        self.operator_filter = operator_filter

    def __str__(self):
        return f"RailDepartureService({self.crs}, {self.operator_filter})"

    def get_board_sync(self) -> DeparturesInfo:
        try:
            settings = Settings(strict=False)
            history = HistoryPlugin()
            client = Client(
                wsdl=self.WSDL,
                settings=settings,
                plugins=[history],
            )

            header = xsd.Element(
                "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken",
                xsd.ComplexType(
                    [
                        xsd.Element(
                            "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue",
                            xsd.String(),
                        ),
                    ]
                ),
            )
            header_value = header(TokenValue=self.api_token)

            res = client.service.GetDepartureBoard(
                numRows=30, crs=self.crs, _soapheaders=[header_value]
            )

            return self.parse_response(res)
        except Exception as e:
            return DeparturesInfo(TransitType.NATIONAL_RAIL, self.crs, [], str(e))

    def parse_response(self, res) -> DeparturesInfo:
        deps = [self.parse_departure(s) for s in res.trainServices.service]
        deps = [d for d in deps if d is not None]
        if self.operator_filter is not None:
            location = f"{res.locationName} ({self.operator_filter})"
        else:
            location = res.locationName
        return DeparturesInfo(TransitType.NATIONAL_RAIL, location, deps)

    def parse_departure(self, res_serviceitem) -> Departure:
        if self.operator_filter is not None:
            if res_serviceitem.operator.lower() != self.operator_filter.lower():
                return None
        api_etd = res_serviceitem.etd.lower()
        if api_etd == "on time":
            status = DepartureStatus.ON_TIME
            etd = "On Time"
        elif api_etd == "cancelled":
            status = DepartureStatus.CANCELLED
            etd = "Cancelled"
        elif api_etd == "delayed":
            status = DepartureStatus.DELAYED
            etd = "Delayed Indefinitely"
        else:
            status = DepartureStatus.DELAYED
            etd = f"Delayed {api_etd}"

        return Departure(
            res_serviceitem.destination.location[0].locationName,
            res_serviceitem.std,
            etd,
            status,
        )

    async def get_board_async(self) -> DeparturesInfo:
        # zeep not playing nice with async, just wrap in worker
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_board_sync)


async def main():
    c = Config("config.json")
    res = await RailDepartureService(
        c.ldbws_api_key(), "WIM", "Thameslink"
    ).get_board_async()
    print(res)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
