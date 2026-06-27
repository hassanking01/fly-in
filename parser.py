from utils import Hub
import sys
from typing import Any, Dict, Optional
from error_classes import (
    HubFormatError,
    HubMetadataError,
    ConnectionMetadataError
    )


def get_hub_details(
        file_line: str,
        is_start_or_end: bool,
        nb_drones: int
        ) -> Dict[str, Any]:
    metadata_format_error = (
        "hub metadata must follow this format: "
        "[zone=<normal|priority|restricted> "
        "color=<valid_color> "
        "max_drones=<int>] "
        "(all fields are optional)"
    )
    line = " ".join(file_line.split())
    values = line.split(" ", 3)
    # name = None
    # x: Optional[str] = None
    # y: Optional[str] = None
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
        if "[" not in raw_metadata or "]" not in raw_metadata:
            raise ValueError("shi idk")
        metadata = raw_metadata.strip("[]").split()
        line = ""
        parsed_metadata = {}
        keys = ["color", "max_drones", "zone"]
        saved_keys: list[str] = []
        zone_types = ["normal", "blocked", "restricted", "priority"]
        for n, i in enumerate(metadata):
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
                key, value = get_key_value("=", line)
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
                        HubMetadataError(
                            "invalid max_drones — max_drones must be valid int"
                            f"\nmetadata format {metadata_format_error}"
                        )

                if key not in keys:
                    raise HubMetadataError(
                        f"unknown metadata key '{key}'"
                        f"\nmetadata format {metadata_format_error}"
                    )
                if key in saved_keys:
                    raise HubMetadataError(
                        f"duplicate key '{key}' —"
                        " each key can only appear once"
                    )
                parsed_metadata.update(
                    {key: value if key != "max_drones" else cased_value}
                )
                line = ""
            if line and n == len(parsed_metadata) - 1:
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
        metadata_result = {
            k: parsed_metadata[k]
            for k in sorted(parsed_metadata.keys())
        }
    else:
        raise HubFormatError(
            f"invalid hub format, expected:"
            " 'name x y' or 'name x y [metadata]', "
            f"got {file_line} "
        )
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


def get_connection_details(edg: str) -> tuple[str, str, str, int]:
    edg = " ".join(edg.split())
    data = edg.split(" ", 1)
    line, src, dest = data[0].split("-")
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
        ):
            is_metadata_good = False
        else:
            key, str_value = get_key_value("=", metadata)
        if is_metadata_good:
            try:
                value = int(str_value)
            except ValueError:
                is_metadata_good = False
        if key != "max_link_capacity":
            is_metadata_good = False
    if not metadata or not is_metadata_good:
        raise ConnectionMetadataError(
            "expected metadata in the form [max_link_capacity=<value: int>]"
        )
    return (line, src, dest, value)


def get_key_value(sep: str, line: str) -> tuple[str, ...]:
    return tuple(map(lambda x: x.strip(), line.split(sep)))


def main_parser() -> Dict[str, Any]:
    map_path = sys.argv[1]
    zone_names = set()
    coordinates = set()
    graph: Dict[Hub, list[Hub]] = {}
    Hubs: dict[str, Hub] = {}
    edges = []
    start_hub = None
    end_hub = None
    nb_drones = -1
    required = {"start_hub", "end_hub", "hub", "connection"}
    next_start = 0
    with open(map_path, mode='r') as file:
        for i, line in enumerate(file, start=1):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            line.lower()
            if (
                    ":" not in line
                    or "nb_drones" not in line
                    or line.count(":") != 1
                    ):
                raise ValueError(f"[{i}]invalide params in nd_drons")

            key, value = get_key_value(":", line)
            try:
                nb_drones = int(value)
                if nb_drones <= 0:
                    raise ValueError(f"{nb_drones}")
            except ValueError as e:
                raise ValueError(f"invalid number of drones: {e}")
            next_start = i
            break
        for i, line in enumerate(file, start=next_start + 1):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            line.lower()
            if ":" not in line or line.count(":") != 1:
                raise ValueError(f"invalide params in line [{i}]")
            key, value = get_key_value(":", line)
            if key not in required:
                raise ValueError(
                    "invalide params in line"
                    f" [{i}] {key} is not a valid key"
                )

            if key == "hub":
                hub_dict = get_hub_details(value, False, 1)
                if hub_dict["name"] in zone_names:
                    raise ValueError(
                        f"error in line [{i}]:"
                        " can't be duplicate name in hubs"
                    )
                elif (hub_dict["x"], hub_dict["y"]) in coordinates:
                    raise ValueError(
                        f"error in line [{i}]:"
                        " same coordinates with different hub"
                    )

                zone_names.add(hub_dict["name"])
                coordinates.add((hub_dict["x"], hub_dict["y"]))
                hub = Hub(**hub_dict)
                graph[hub] = []
                Hubs[hub.name] = hub
            elif key == "connection":
                edges += [f"{i}-{value}"]
            elif key == "start_hub":
                hub_dict = get_hub_details(value, True, nb_drones)
                if hub_dict["name"] in zone_names:
                    raise ValueError(
                        f"error in line [{i}]:"
                        " can't be duplicate name in hubs"
                    )

                elif (hub_dict["x"], hub_dict["y"]) in coordinates:
                    raise ValueError(
                        f"error in line [{i}]:"
                        " same coordinates with different hub"
                    )

                zone_names.add(hub_dict["name"])
                coordinates.add((hub_dict["x"], hub_dict["y"]))
                start_hub = Hub(**hub_dict)
                graph[start_hub] = []
                Hubs[start_hub.name] = start_hub

            elif key == "end_hub":
                hub_dict = get_hub_details(value, True, nb_drones)
                if hub_dict["name"] in zone_names:
                    raise ValueError(
                        f"error in line [{i}]:"
                        " can't be duplicate name in hubs"
                    )
                elif (hub_dict["x"], hub_dict["y"]) in coordinates:
                    raise ValueError(
                        f"error in line [{i}]:"
                        " same coordinates with different hub"
                    )
                zone_names.add(hub_dict["name"])
                coordinates.add((hub_dict["x"], hub_dict["y"]))
                end_hub = Hub(**hub_dict)
                end_hub.is_goal_hub = True
                graph[end_hub] = []
                Hubs[end_hub.name] = end_hub
        for edg in edges:
            line, src_name, dest_name, mlc = get_connection_details(edg)
            if src_name not in zone_names:
                raise ValueError(
                    f"error in line [{line}]: {src_name} is not hub"
                )
            if dest_name not in zone_names:
                raise ValueError(
                    f"error in line [{line}]: {dest_name} is not hub"
                )
            src = Hubs[src_name]
            dest = Hubs[dest_name]
            src.connections[dest] = {
                "max_link_capacity": mlc,
                "on_road": 0
            }
            dest.connections[src] = {
                "max_link_capacity": mlc,
                "on_road": 0
            } 
            graph[src] += [dest]
            graph[dest] += [src]
        return {
            "graph": graph,
            "start": start_hub,
            "end": end_hub,
            "nb_drones": nb_drones
        }
