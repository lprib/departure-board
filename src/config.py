import json
import logging

import departure_service
import ldbws_api
import tfl_api

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, filename):
        with open(filename, "r") as f:
            self.c = json.load(f)
        logger.info(self.c)

    def ldbws_api_key(self) -> str:
        return self.c["ldbws_api_key"]

    def board_service(self, board_conf) -> departure_service.DepartureService:
        typ = board_conf["type"]
        if typ == "ldbws":
            if "operator" in board_conf:
                op = board_conf["operator"]
            else:
                op = None
            return ldbws_api.RailDepartureService(
                self.ldbws_api_key(), board_conf["crs"], op
            )
        elif typ == "tfl":
            return tfl_api.TflStopPointService(board_conf["naptan"])
        else:
            raise Exception(f"unknown board type {typ}")

    def board_services(self) -> list[departure_service.DepartureService]:
        return [self.board_service(conf) for conf in self.c["boards"]]
