import re
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
import osm2geojson
import requests

from location.models import Location


class Command(BaseCommand):
    help = "Fetches, Cleans and Stores the data from OSM Overpass."

    def handle(self, *args, **options):
        overpass_url = "https://overpass-api.de/api/interpreter"

        overpass_query = """
        [out:json][bbox:27.6138,85.2202,27.7980,85.4437][timeout:60];
        (
            nwr["tourism"];
            nwr["historic"];
            nwr["leisure"];
        );
        out geom;
        >;
        out skel qt;
        """

        response = requests.post(
            overpass_url,
            data={"data": overpass_query},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            print(f"Error while making request: {response.status_code} {response.text}")
            return

        osm_json = response.json()
        osm_data = osm2geojson.json2shapes(osm_json)

        locations = []

        for data in osm_data:
            try:
                tags = data["properties"]["tags"]
                geom_shape = data["shape"]
            except KeyError as e:
                continue

            lon, lat, geom = self.get_geometry(geom_shape)

            try:
                locations.append(
                    Location(
                        category=self.get_category(tags),
                        name=self.get_name(tags),
                        description=self.get_description(tags),
                        lon=lon,
                        lat=lat,
                        geom=geom,
                        wheelchair=self.get_wheelchair(tags),
                        toilet=self.get_toilet(tags),
                        wifi=self.get_wifi(tags),
                        opening_hours=self.get_opening_hours(tags),
                        raw_tags=tags,
                    )
                )
            except Exception as e:
                pass

        self.stdout.write(
            self.style.SUCCESS(f"Finished processing {len(locations)} locations...")
        )
        Location.objects.bulk_create(locations, batch_size=256)
        self.stdout.write(self.style.SUCCESS("Locations populated successfully..."))

    def get_name(self, tags: dict) -> str:
        for key, value in tags.items():
            if key.startswith("name") and value:
                return value.strip()
        return "Unknown"

    def get_category(self, tags: dict) -> str:
        mappings = {
            "religious": "religious",
            "temple": "religious",
            "place_of_worship": "religious",
            "palace": "palace",
            "castle": "palace",
            "museum": "museum",
            "park": "park",
            "monument": "monument",
            "memorial": "monument",
            "stone_tap": "monument",
            "restaurant": "restaurant",
            "cafe": "restaurant",
            "hotel": "accommodation",
            "guest_house": "accommodation",
            "apartment": "accommodation",
            "hostel": "accommodation",
        }
        categories = {
            mappings.get(val, "other")
            for key in [
                "tourism",
                "historic",
                "amenity",
                "building",
                "leisure",
            ]
            if key in tags and (val := tags[key])
        }

        if categories:
            return categories.pop()

        return "other"

    def get_geometry(self, geom_shape):
        centroid = geom_shape.centroid
        lat, lon = centroid.y, centroid.x
        geom = GEOSGeometry(geom_shape.wkt, srid=4326)
        return lat, lon, geom

    def get_description(self, tags: dict) -> bool:
        options = {val.lower() for key, val in tags.items() if "description" in key}
        try:
            options.pop()
        except KeyError:
            return None

    def get_wheelchair(self, tags: dict) -> bool:
        options = {val.lower() for key, val in tags.items() if "wheelchair" in key}
        try:
            return "no" not in options.pop()
        except KeyError:
            return False

    def get_toilet(self, tags: dict) -> bool:
        options = {val.lower() for key, val in tags.items() if "toilet" in key}
        try:
            return "no" not in options.pop()
        except KeyError:
            return False

    def get_wifi(self, tags: dict) -> bool:
        options = {
            val.lower()
            for key, val in tags.items()
            if "internet_access" in key or "wlan" in key
        }
        try:
            return "no" not in options.pop()
        except KeyError:
            return False

    def get_opening_hours(self, tags: dict) -> dict:
        opening_str = tags.get('opening_hours', 'Mo-Fri 09:00-17:00')

        day_map = {
            'Mo': 'monday',
            'Tu': 'tuesday',
            'We': 'wednesday',
            'Th': 'thursday',
            'Fr': 'friday',
            'Sa': 'saturday',
            'Su': 'sunday'
        }

        days_map = {
            'Mo-Su': 'Mo,Tu,We,Th,Fr,Sa,Su',
            'Su-Fr': 'Su,Mo,Tu,We,Th,Fr',
            'Su-Sa': 'Su,Mo,Tu,We,Th,Fr,Sa',
            'Mo-Fr': 'Mo,Tu,We,Th,Fr',
            'Sa-Su': 'Sa,Su',
            'Th-Mo': 'Th,Fr,Sa,Su,Mo',
        }

        # Default: all days closed
        result = {day: None for day in day_map.values()}

        if opening_str == '24/7':
            for day in result:
                result[day] = '00:00-24:00'
            return result

        # Find all day groups and times
        pattern = r'([A-Za-z,-]+)\s*([\d:]{2,5}-[\d:]{2,5})'
        matches = re.findall(pattern, opening_str)

        if not matches and re.match(r'^[\d:]{2,5}-[\d:]{2,5}$', opening_str):
            # Only time, all days
            for day in result:
                result[day] = opening_str
            return result

        for days, hours in matches:
            days = days.strip()
            days = days_map.get(days, days)
            for day in days.split(','):
                day = day.strip()
                if day in day_map:
                    result[day_map[day]] = hours

        return result
