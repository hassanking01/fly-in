from utils import Hub, Map, Drone
import sys

def get_hub_details(value: str, is_start_or_end: bool, nb_drones: int):
    value = value.split()
    value = list( filter( lambda x:x,  map(lambda x: x.strip(), value)))
    value = " ".join(value)
    value = value.split(" ", 3)
    name = None
    x = None
    y = None
    metadata = None
    if len(value) == 3:
        name, x, y = list(map(lambda x: x.strip(), value))
        metadata = {"color":None, "max_drones":nb_drones if is_start_or_end else 1, "zone":"normal"}
    elif len(value) == 4:
        name , x , y , metadata = list( filter( lambda x:x,  map(lambda x: x.strip(), value)))
        if "[" not in metadata or "]" not in metadata:
            raise ValueError("shi idk")
        metadata = metadata.strip("[").strip("]").split()
        result = {}
        
        for item in metadata:
            item = item.strip()
            if not item:
                continue
            key, val = list(map(lambda x: x.strip(), item.split("=")))
            if not key or not val:
                raise ValueError("error the metadata key value peers should be exactly like this: key=value")
            if key ==  "zone":
                if result.get(key):
                    raise ValueError("duplicated metadata")
                else:
                    result[key] = val
            elif key == "color":
                if result.get(key):
                    raise ValueError("duplicated metadata")
                else:
                    result[key] = val
            elif key == "max_drones":
                print(key, val)
                if result.get(key):
                    raise ValueError("duplicated metadata")
                else:
                    try:
                        result[key] = int(val)
                    except ValueError as error:
                        raise ValueError("not int value in max_drones")
            else:
                raise ValueError(f"{key}:not a valid key in metadata")
        metadata = result
        if not metadata.get("zone"):
            metadata["zone"] = "normal"
        if not metadata.get("color"):
            metadata["color"] = None
        if not metadata.get("max_drones"):
            metadata["max_drones"] = nb_drones if is_start_or_end else 1
        if is_start_or_end and metadata["max_drones"] < nb_drones:
            raise ValueError("number of drones in start and end should be equal to total drones")
        metadata = {k: metadata[k] for k in sorted(metadata.keys())}
    else:
        raise ValueError("shi idk")
    if not name:
        raise  ValueError("not should not be empty string")

    try:
        x = int(x)
    except ValueError:
        raise ValueError(f"x value in {name} should be int")

    try:
        y = int(y)
    except ValueError:
        raise ValueError(f"x value in {name} should be int")


    result = {"name":name, "x":x, "y":y, **metadata}
    return result 


def main_parser():
    if len(sys.argv) != 2:
        raise ValueError("invalide number of arguments")
    map_path = sys.argv[1]
    zone_names = set()
    coordinates = set()
    graph = {}
    edges = []
    start_hub = None
    end_hub = None
    nb_drones = -1
    nb_drones_flag = False
    start_flag = False
    end_flag = False
    required = {"start_hub", "end_hub", "hub", "connection"}
    next_start = 0
    with open(map_path, mode='r') as file:
        for i , line in enumerate(file, start=1):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            line.lower()
            if "#" in line:
                line = line.split("#")[0]
            if ":" not in line or "nb_drones" not in line or line.count(":") != 1:
                raise ValueError(f"[{i}]invalide params in nd_drons")
            key, value = list(map(lambda string: string.strip(), line.split(":")))
            try:
                nb_drones = int(value)
                if nb_drones <= 0:
                    raise ValueError(f"{nb_drones}")
                nb_drones_flag = True
            except ValueError as e:
                raise ValueError(f"invalid number of drones: {e}" )
            next_start = i
            break
        for i, line in enumerate(file, start=next_start + 1):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            line.lower()
            if "#" in line:
                line = line.split("#")[0]
            if ":" not in line or line.count(":") != 1:
                raise ValueError(f"invalide params in line [{i}]")
            key , value = list(map(lambda string: string.strip(), line.split(":")))
            if key not in required:
                raise ValueError(f"invalide params in line [{i}] {key} is not a valid key")
            if key == "hub":
                hub = get_hub_details(value, False, 1)
                if hub["name"] in zone_names:
                    raise ValueError(f"error in line [{i}]: can't be duplicate name in hubs")
                elif (hub["x"], hub["y"]) in coordinates:
                    raise ValueError(f"error in line [{i}]: same coordinates with different hub")
                zone_names.add(hub["name"])
                coordinates.add((hub["x"], hub["y"]))
                graph[Hub(**hub)] = []
            elif key == "connection":
                edges += [f"{i}-{value}"]
            elif key == "start_hub":
                hub = get_hub_details(value, True, nb_drones)
                if hub["name"] in zone_names:
                    raise ValueError(f"error in line [{i}]: can't be duplicate name in hubs")
                elif (hub["x"], hub["y"]) in coordinates:
                    raise ValueError(f"error in line [{i}]: same coordinates with different hub")
                zone_names.add(hub["name"])
                coordinates.add((hub["x"], hub["y"]))
                start_hub = Hub(**hub) 
                start_hub.current_drones_count = nb_drones
                graph[start_hub] = []

            elif key == "end_hub":
                hub = get_hub_details(value, True, nb_drones)
                if hub["name"] in zone_names:
                    raise ValueError(f"error in line [{i}]: can't be duplicate name in hubs")
                elif (hub["x"], hub["y"]) in coordinates:
                    raise ValueError(f"error in line [{i}]: same coordinates with different hub")
                zone_names.add(hub["name"])
                coordinates.add((hub["x"], hub["y"]))
                end_hub = Hub(**hub) 
                graph[end_hub] = []
        for edg in edges:

            line, src, dest = map(lambda x: x.strip(), edg.split("-"))
            if src not in zone_names:
                raise ValueError(f"error in line [{line}]: {src} is not hub")
            if dest not in zone_names:
                raise ValueError(f"error in line [{line}]: {dest} is not hub")
            src = [ key for key in graph if key.name == src][0]
            dest = [key for key in graph if key.name == dest][0]
            
            graph[src] += [dest]
            graph[dest] += [src]
        return {"graph":graph, "start": start_hub, "end": end_hub, "nb_drones": nb_drones}



if __name__ == "__main__":
    try:

        main_parser()
    except Exception as e:
        print(e)