import enum


class TransitType(enum.Enum):
    NATIONAL_RAIL = 0
    BUS = 1


class DepartureStatus(enum.Enum):
    ON_TIME = 0
    DELAYED = 1
    CANCELLED = 2


class Departure:
    def __init__(
        self, to: str, std: str, etd: str, status: DepartureStatus, arrival_time=None
    ):
        self.to = to
        self.std = std
        self.etd = etd
        self.status = status
        self.arrival_time = arrival_time

    def __str__(self) -> str:
        return f"{self.std} {self.to}: {self.etd}"


class DeparturesInfo:
    def __init__(
        self,
        transit: TransitType,
        location: str,
        departures: list[Departure],
        failtext: str | None = None,
    ):
        self.transit = transit
        self.location = location
        self.departures = departures
        self.failtext = failtext

    def __str__(self) -> str:
        return f"{self.transit.name} {self.location}\n" + "\n".join(
            [str(d) for d in self.departures]
        )


class DepartureService:
    def get_board_sync(self) -> DeparturesInfo:
        raise NotImplementedError()

    async def get_board_async(self) -> DeparturesInfo:
        raise NotImplementedError()
