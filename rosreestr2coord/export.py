import os
import csv
import json
import xml.etree.cElementTree as ET


def make_output(output, file_name, file_format, out_path=""):
    out_path = out_path or file_format
    path = os.path.join(os.path.abspath(output), out_path)
    print(f"Creating directory: {path}")
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f"{file_name}.{file_format}")
    print(f"File will be saved to: {file_path}")
    return file_path


def _write_csv_row(writer, area, header=False):
    try:
        geometry = area.feature.get('geometry', {})
        coords = geometry.get('coordinates', [])

        transformed_coords = []
        for geom in coords:
            for poly in geom:
                print(poly)
                if isinstance(poly, list):
                    poly[0], poly[1] = poly[1], poly[0]
                    transformed_coords.append(poly)
        if header:
            writer.writerow(["longitude", "latitude"])

        for coord in transformed_coords:
            writer.writerow([coord[0], coord[1]])

    except Exception as er:
        print(f"Error: {er}")


def area_csv_output(output, area):
    path = make_output(output, area.file_name, "csv")
    print(f"Writing CSV to: {path}")
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        _write_csv_row(writer, area, header=True)


def batch_csv_output(output, areas, file_name):
    path = make_output(output, file_name, "csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for i, area in enumerate(areas):
            _write_csv_row(writer, area, header=(i == 0))
    return path


def batch_json_output(output, areas, file_name, with_attrs=True, crs_name="EPSG:4326"):
    features = [a.to_geojson_poly(with_attrs, dumps=False) for a in areas if a.to_geojson_poly(with_attrs, dumps=False)]
    geojson = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": crs_name}},
        "features": features,
    }
    path = make_output(output, file_name, "geojson")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=4)
    return path


def area_json_output(output, area, with_attrs=True):
    geojson = area.to_geojson_poly(with_attrs)
    if geojson:
        path = make_output(output, area.file_name, "geojson")
        with open(path, "w", encoding="utf-8") as f:
            f.write(geojson)
    return geojson


def coords2geojson(coords, geom_type, crs_name, attrs=None):
    if not coords:
        return False

    features = []
    if geom_type.upper() == "POINT":
        for geom in coords:
            for poly in geom:
                for x, y in poly:
                    features.append({
                        "type": "Feature",
                        "properties": {"hole": False},
                        "geometry": {"type": "Point", "coordinates": [x, y]},
                    })
    elif geom_type.upper() == "POLYGON":
        multi_polygon = [[[poly + [poly[0]]] for poly in geom] for geom in coords]
        return {
            "type": "Feature",
            "properties": attrs or {},
            "geometry": {"type": "MultiPolygon", "coordinates": multi_polygon},
            "crs": {"type": "name", "properties": {"name": crs_name}},
        }

    return {"type": "FeatureCollection", "features": features,
            "crs": {"type": "name", "properties": {"name": crs_name}}}


def coords2kml(coords, attrs):
    if not coords:
        return False

    kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, "Document")
    folder = ET.SubElement(doc, "Folder")
    ET.SubElement(folder, "name").text = attrs.get("label") or attrs.get("options", {}).get("cad_num", "")

    placemark = ET.SubElement(folder, "Placemark")
    style = ET.SubElement(placemark, "Style")
    ET.SubElement(ET.SubElement(style, "LineStyle"), "color").text = "ff0000ff"
    ET.SubElement(ET.SubElement(style, "PolyStyle"), "fill").text = "0"

    multi_geometry = ET.SubElement(placemark, "MultiGeometry")
    for geom in coords:
        polygon = ET.SubElement(multi_geometry, "Polygon")
        for j, poly in enumerate(geom):
            boundary = ET.SubElement(polygon, "innerBoundaryIs" if j else "outerBoundaryIs")
            ET.SubElement(ET.SubElement(boundary, "LinearRing"), "coordinates").text = " ".join(
                ",".join(map(str, point)) for point in (poly + [poly[0]])
            )

    return ET.ElementTree(kml)
