import requests
import xml.etree.ElementTree as ET
import csv

def get_data_from_api():
    game_ids = ['68448', '173346', '246784', '242302', '269725']

    try:
        api_url = f"https://boardgamegeek.com/xmlapi2/thing?id={','.join(game_ids)}&stats=1"
        response = requests.get(api_url)
        if response.status_code == 200:
            return ET.fromstring(response.content)
        else:
            print(f"Erreur lors de la requête API: {response.status_code}")
            return None
        
    except requests.RequestException as e:
        print(f"Erreur de connexion: {e}")
        return None
    
    except ET.ParseError as e:
        print(f"Erreur de parsing XML: {e}")
        return None

def parse_xml_file(xml_path):
    try:
        tree = ET.parse(xml_path)
        return tree.getroot()
    
    except ET.ParseError as e:
        print(f"Erreur lors du parsing du fichier XML local: {e}")
        return None
    except FileNotFoundError:
        print(f"Le fichier XML '{xml_path}' n'a pas été trouvé")
        return None
    except Exception as e:
        print(f"Erreur inattendue lors de la lecture du fichier XML: {e}")
        return None

def extract_game_data(root):
    games_data = []
    
    for item in root.findall('.//item'):
        game = {}
        
        name = item.find('.//name[@type="primary"]')
        game['title'] = name.get('value') if name is not None else "Unknown"
        
        year = item.find('.//yearpublished')
        game['year'] = year.get('value') if year is not None else "Unknown"
        
        minplayers = item.find('.//minplayers')
        maxplayers = item.find('.//maxplayers')
        min_p = minplayers.get('value') if minplayers is not None else "?"
        max_p = maxplayers.get('value') if maxplayers is not None else "?"
        
        game['players'] = min_p if min_p == max_p else f"{min_p}-{max_p}"
        
        mintime = item.find('.//minplaytime')
        maxtime = item.find('.//maxplaytime')
        min_t = mintime.get('value') if mintime is not None else "?"
        max_t = maxtime.get('value') if maxtime is not None else "?"
        
        game['playtime'] = f"{min_t}min" if min_t == max_t else f"{min_t}-{max_t}min"
        
        rating = item.find('.//statistics/ratings/average')
        if rating is not None:
            avg = float(rating.get('value'))
            game['average'] = str(round(avg))  
        else:
            game['average'] = "0"
        
        games_data.append(game)
    
    return games_data


def write_to_csv(games_data, output_file):
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')           
            writer.writerow(['TITLE', 'PUBLISHED YEAR', 'NUMBER PLAYERS', 'PLAY TIME', 'AVERAGE'])
            for game in games_data:
                writer.writerow([
                    game['title'],
                    game['year'],
                    game['players'],
                    game['playtime'],
                    game['average']
                ])
                
        print(f"Le fichier CSV '{output_file}' a été créé avec succès.")
        
    except IOError as e:
        print(f"Erreur lors de l'écriture du fichier CSV: {e}")
    except Exception as e:
        print(f"Erreur inattendue lors de l'écriture du fichier CSV: {e}")


def main():
    # Essayer d'abord l'API
    xml_data = get_data_from_api()
    
    if xml_data is None:
        # En cas d'échec, utiliser le fichier XML local
        xml_data = parse_xml_file("games.xml")
    
    games_data = extract_game_data(xml_data)
    write_to_csv(games_data, "ludotheque.csv")

if __name__ == "__main__":
    main()
