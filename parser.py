from utils import Hub
import sys
from typing import Any, Dict, Optional
from error_classes import (
    ParserError,
    HubFormatError,
    HubMetadataError,
    ConnectionMetadataError,
    ConnectionEdgError
    )

class Parser:

    def __init__(self):
        self.map_path = sys.argv[1]
        self.zone_names = set()
        self.coordinates = set()
        self.graph: Dict[Hub, list[Hub]] = {}
        self.Hubs: dict[str, Hub] = {}
        self.connections = set()
        self.start_end_check = {"start_hub": False,"end_hub": False }
        self.start_hub = None
        self.end_hub = None
        self.nb_drones = 0
        self.required = {"start_hub", "end_hub", "hub", "connection"}

    def get_hub_details(
            self,
            file_line: str,
            is_start_or_end: bool,
            nb_drones: int
            ) -> Dict[str, Any]:
        metadata_format_error = (
            "hub metadata must follow this format:"
            " [zone=<normal|priority|restricted>"
            " color=<valid_color>"
            " max_drones=<int>]"
            " (all fields are optional)"
        )
        line = " ".join(file_line.split())
        values = line.split(" ", 3)
        metadata: list[str] = []
        parsed_metadata: Optional[Dict[str, Any]] = None

        if len(values) == 3:
            name, str_x, str_y = values
            parsed_metadata = {
                "color": "blue",
                "max_drones": nb_drones if is_start_or_end else 1,
                "zone": "normal"
            }
        elif len(values) == 4:
            name, str_x, str_y, raw_metadata = values
            if (
                raw_metadata[0] != "["
                or raw_metadata[-1] != "]"
                or raw_metadata.count("[") != 1
                or raw_metadata.count("]") != 1
            ):
                if raw_metadata[0] != "[":
                    if "[" not in raw_metadata:
                        error = "missing opening bracket '['"
                    else :
                        error = "opening bracket '[' not in the beginning"
                        
                        
                elif raw_metadata[-1] != "]":
                    if "]" not in raw_metadata:
                        error = "missing closing bracket ']'"
                    else:
                        error = "closing bracket ']' not on the end"
                elif raw_metadata.count("[") > 1:
                    error = "multiple opening brackets '['"
                elif raw_metadata.count("]") > 1:
                    error = "multiple closing brackets ']'"
                raise HubMetadataError(f"{error}\n{metadata_format_error}")
            metadata = raw_metadata.strip("[]").split()
            line = ""
            parsed_metadata = {}
            keys = ["color", "max_drones", "zone"]
            zone_types = ["normal", "blocked", "restricted", "priority"]
            for index, i in enumerate(metadata):
                if (
                    not line and i[0] == "="
                    or line and "=" in line and "=" in i
                    or "=" in i and i.count("=") != 1
                    or line and "=" not in line and i.count("=") != 1
                    or line and line[-1] != "=" and i[0] != "="
                ):
                    raise HubMetadataError(
                        f"invalid metadata format — {metadata_format_error}"
                    )
                line += i
                if line and "=" in line and line[-1] != "=":
                    key, value = self.get_key_value("=", line)
                    if key == "zone":
                        if value not in zone_types:
                            raise HubMetadataError(
                                f"invalid zone '{value}', "
                                f"must be one of {set(zone_types)}"
                            )
                    if key == "max_drones":
                        try:
                            cased_value = int(value)
                        except ValueError:
                            raise HubMetadataError(
                                f"invalid max_drones — max_drones must be valid int got '{value}'\n"
                                f"metadata format {metadata_format_error}"
                            )
                        if cased_value <= 0:
                            raise HubMetadataError(
                                f"max_drones must be a positive integer, got '{cased_value}'")

                    if key not in keys:
                        raise HubMetadataError(
                            f"unknown metadata key '{key}'"
                            f" metadata format {metadata_format_error}"
                        )
                    if key in parsed_metadata:
                        raise HubMetadataError(
                            f"duplicate key '{key}' —"
                            " each key can only appear once"
                        )
                    parsed_metadata.update(
                        {key: value if key != "max_drones" else cased_value}
                    )
                    line = ""
                if line and index == len(metadata) - 1:
                    if "=" in line or line in keys:
                        raise HubMetadataError(
                            f"missing value for key '{line.split('=')[0]}'"
                            f" — {metadata_format_error}")
                    else:
                        HubMetadataError(
                            f"unknown key '{line}' — {metadata_format_error}"
                        )
            if "zone" not in parsed_metadata:
                parsed_metadata["zone"] = "normal"
            if "color" not in parsed_metadata:
                parsed_metadata["color"] = "blue"
            if "max_drones" not in parsed_metadata:
                parsed_metadata["max_drones"] = 1
            if is_start_or_end and parsed_metadata["max_drones"] < nb_drones:
                parsed_metadata["max_drones"] = nb_drones
        else:
            raise HubFormatError(
                f"invalid hub format, expected:"
                " 'name x y' or 'name x y [metadata]', "
                f"got {file_line} "
            )
        metadata_result = {
            k: parsed_metadata[k]
            for k in sorted(parsed_metadata.keys())
        }
        try:
            x = int(str_x)
        except ValueError:
            raise HubFormatError(
                f"invalid x coordinate for hub '{name}',"
                f" expected int, got '{str_x}'"
            )

        try:
            y = int(str_y)
        except ValueError:
            raise HubFormatError(
                f"invalid y coordinate for hub '{name}',"
                f" expected int, got '{str_y}'"
            )

        result = {
            "name": name,
            "x": x,
            "y": y,
            **metadata_result
        }
        return result


    def get_connection_details(self, edg: str) -> tuple[str, str, str, int]:
        edg = " ".join(edg.split())
        data = edg.split(" ", 1)
        if "-" not in data[0]:
            raise ConnectionEdgError(
                f"zone names must be separated by '-', got '{data[0]}'"
                )
        if data[0].count("-") > 1:
            raise ConnectionEdgError(
                f"expected exactly one '-' separator, got '{data[0]}'"
            )
        if data[0][0] == "-" or data[0][-1] == "-":
            raise ConnectionEdgError(
                f"zone name cannot be empty in '{data[0]}'"
            )
        src, dest = get_key_value(sep="-", line=data[0])
        if src == dest:
            raise ConnectionEdgError(
                f"source and destination zones must be different: '{src}'"
            )

        if len(data) == 1:
            metadata = "max_link_capacity=1"
        else:
            metadata = data[1]
            if metadata[0] != "[":
                raise ConnectionMetadataError(
                    f"invalid metadata opening expected '[', got '{metadata[0]}'"
                )

            if metadata[-1] != "]":
                raise ConnectionMetadataError(
                    f"invalid metadata closing expected ']', got '{metadata[-1]}'"
                )

            metadata = metadata.strip("[]").strip()
        is_metadata_good = True
        if metadata:

            if (
                "=" not in metadata
                or metadata[0] == "="
                or metadata[-1] == "="
                or metadata.count("=") > 1
                or metadata.count("[")
                or metadata.count("]")
            ):
                is_metadata_good = False
            else:
                key, str_value = get_key_value("=", metadata)
            if is_metadata_good:
                value = 0
                try:
                    value = int(str_value)
                except ValueError:
                    is_metadata_good = False
                if value <= 0 and key == "max_link_capacity":
                    raise ConnectionMetadataError(
                        f"max_link_capacity must be a positive integer, got '{str_value}'"
                    )
            if key != "max_link_capacity":
                is_metadata_good = False
        if not metadata or not is_metadata_good:
            raise ConnectionMetadataError(
                "expected metadata in the form [max_link_capacity=<value: int>]"
            )
        return (src, dest, value)


    def get_key_value(self, sep: str, line: str) -> tuple[str, ...]:
        return tuple(map(lambda x: x.strip(), line.split(sep)))

    def get_nb_drones(self, value: str):
        try:
            self.nb_drones = int(value)
            valid = self.nb_drones > 0
        except ValueError:
            valid = False
        if not valid:
            raise ParserError()


    def main_parser(self) -> Dict[str, Any]:
        next_start = 0
        with open(self.map_path, mode='r') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                line.lower()
                if (
                        ":" not in line
                        or line.count(":") != 1
                        ):
                    if ":" not in line:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"missing ':' separator, got '{line}'"
                        )
                    if line.count(":") != 1:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"expected exactly one ':', got '{line}'"
                        )
                key, value = self.get_key_value(":", line)
                if not self.nb_drones:
                    if key != "nb_drones":
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"first line must be 'nb_drones: <number>', got '{line}'"
                        )
                    try:
                        self.get_nb_drones(value)
                    except ParserError:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"nb_drones must be a positive integer, got '{value}'"
                        )
                else:
                    if key == "nb_drones":
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"nb_drones must be a positive integer, got '{value}'"
                        )
                if key not in self.required:
                    raise ParserError(
                        line_number,
                        f"ParserError Error in Line",
                        f"unknown keyword '{key}', expected one of [start_hub, end_hub, hub, connection]"
                    )

                if (
                    key == "hub"
                    or key == "start_hub"
                    or key == "end_hub"):
                    try:
                        if (
                            key == "end_hub"
                            or key == "start_hub"
                        ):
                            if self.start_end_check[key]:
                                raise ParserError(
                                        line_number,
                                        f"ParserError Error in Line",
                                        f"duplicated [{key}] Only one '{key}' is allowed per map"
                                    )
                            self.start_end_check[key] = True
                            hub_dict = self.get_hub_details(value, True, self.nb_drones)
                        else:
                            hub_dict = self.get_hub_details(value, False, 1)
                    except HubFormatError as e:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"invalid hub definition — {str(e)}"
                        )
                    except HubMetadataError as e:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"invalid hub metadata — {str(e)}"
                        )
                    if hub_dict["name"] in self.zone_names:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"duplicate zone name '{hub_dict['name']}"
                        )
                    if "-" in hub_dict["name"]:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"zone name '{hub_dict['name']}' cannot contain '-'"                        
                        )
                    elif (hub_dict["x"], hub_dict["y"]) in self.coordinates:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"zone '{hub_dict['name']}' shares coordinates "
                            f"({hub_dict['x']}, {hub_dict['y']}) with an existing zone"
                            )
                    self.zone_names.add(hub_dict["name"])
                    self.coordinates.add((hub_dict["x"], hub_dict["y"]))
                    hub = Hub(**hub_dict)
                    self.graph[hub] = []
                    self.Hubs[hub.name] = hub
                    if key == "start_hub":
                        self.start_hub = hub
                    if key == "end_hub":
                        self.end_hub = hub
                        self.end_hub.is_goal_hub = True
                elif key == "connection":
                    try:
                        src_name, dest_name, mlc = self.get_connection_details(value)
                    except ConnectionEdgError as e:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"invalid connection edge — {str(e)}"
                        )
                    except ConnectionMetadataError as e:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"invalid connection metadata — {str(e)}"
                        )
                    if src_name not in self.zone_names:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"unknown zone '{src_name}' — "
                            f"zone must be defined before being used in a connection"
                        )
                    if dest_name not in self.zone_names:
                            raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"unknown zone '{dest_name}' — "
                            f"zone must be defined before being used in a connection"
                        )
                    connection = tuple(sorted((src_name, dest_name)))
                    if connection in self.connections:
                        raise ParserError(
                            line_number,
                            f"ParserError Error in Line",
                            f"duplicate connection '{src_name}-{dest_name}' — "
                            f"connection already defined"   
                        )
                    self.connections.add(connection)
                    src = self.Hubs[src_name]
                    dest = self.Hubs[dest_name]
                    src.connections[dest] = {
                        "max_link_capacity": mlc,
                        "on_road": 0
                    }
                    dest.connections[src] = {
                        "max_link_capacity": mlc,
                        "on_road": 0
                    } 
                    self.graph[src] += [dest]
                    self.graph[dest] += [src]
            if next_start == 0:
                raise ParserError(
                        next_start + 1,
                        f"ParserError Error in Line",
                        "the map file is empty"
                )
            return {
                "graph": self.graph,
                "start": self.start_hub,
                "end": self.end_hub,
                "nb_drones": self.nb_drones
            }
