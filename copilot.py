#copilot.py

import json
import csv
from datetime import datetime, timedelta, timezone
from geopy.distance import geodesic
import pydoc

def is_within_radius(target_location, current_location, radius):
    return geodesic(target_location, current_location).meters <= float(radius)

def convert_iso8601_string_to_timestamp(iso8601_string):
    date = datetime.fromisoformat(iso8601_string.replace("Z", "+00:00"))
    return int(date.replace(tzinfo=timezone.utc).timestamp() * 1e6)

def get_user_input():
    target_location = ()
    try:
        with open('config.txt', 'r') as file:
            config_data = file.read().splitlines()
            start_date, end_date, target_lat, target_lon, radius = config_data
            target_location = (float(target_lat), float(target_lon))
            print(config_data, "Target Location=", target_location)
    except FileNotFoundError:
        start_date = input('Enter start date (mm/dd/yyyy): ')
        end_date = input('Enter end date (mm/dd/yyyy): ')
        target_lat = float(input('Enter target latitude: '))
        target_lon = float(input('Enter target longitude: '))
        radius = float(input('Enter radius in meters: '))
        print(start_date, end_date, target_location, radius)
    
    return start_date, end_date, (target_lat, target_lon), radius

def load_json_data(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        locations = data['locations']
        
        for loc in locations:
            loc['latitude'] = loc['latitudeE7'] / 1e7
            loc['longitude'] = loc['longitudeE7'] / 1e7
            loc['timestamp'] = convert_iso8601_string_to_timestamp(loc['timestamp'])
    
    return data

def convert_date_to_timestamp(date_string):
    date = datetime.strptime(date_string, "%m/%d/%Y").replace(tzinfo=timezone.utc)
    return int(date.timestamp() * 1e6)

def main():
    start_date, end_date, target_location, radius = get_user_input()
    start_timestamp = convert_date_to_timestamp(start_date)
    end_timestamp = convert_date_to_timestamp(end_date)
    
    total_time = timedelta(0)
    with open('Records.json', 'r') as file:
        data = json.load(file)
        locations = data['locations']
        locations_checked = 0
        
        for i in range(len(locations) - 1):
            loc = locations[i]
            locations_checked += 1
            lat = loc.get('latitudeE7')
            if lat is not None:
                lat /= 1e7
            lon = loc.get('longitudeE7') 
            if lon is not None:
                lon /= 1e7
            timestamp = convert_iso8601_string_to_timestamp(loc['timestamp'])
            
            if start_timestamp <= timestamp <= end_timestamp:
                if is_within_radius(target_location, (lat, lon), radius):
                    next_timestamp = convert_iso8601_string_to_timestamp(locations[i + 1]['timestamp'])
                    time_spent = timedelta(microseconds=next_timestamp - timestamp)
                    total_time += time_spent
                    print(f"Time spent at this location: {time_spent}")
                    print(f"Total time so far: {total_time}")
                
    
    print(f'Total time spent at the location: {total_time}')
    print(f'Lines checked: {locations_checked}')
    
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Start Date', 'End Date', 'Target Location', 'Radius', 'Total Time Spent'])
        writer.writerow([start_date, end_date, target_location, radius, total_time])

if __name__ == '__main__':
    main()

pydoc.writedoc('copilot')