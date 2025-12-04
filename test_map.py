from modules.visualizer import Visualizer

print('Testing updated map data...')
viz = Visualizer()
map_data = viz.get_map_data()

print(f'Total locations: {len(map_data["locations"])}')
print('\nCities and their case counts:')
for loc in map_data['locations']:
    print(f'  {loc["name"]}: {loc["cases"]} cases')

print(f'\nMessage: {map_data["message"]}')