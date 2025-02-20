import json
import argparse
import sys
from typing import List, Optional, Dict
import yaml
import csv
from pathlib import Path


def parse_musicians_string(musicians_str: str) -> List[tuple[str, str]]:
    """Parse a string of format 'instrument1:name1; instrument2:name2' into list of tuples"""
    if not musicians_str or musicians_str.isspace():
        return []

    musicians = []
    pairs = musicians_str.split(';')
    for pair in pairs:
        pair = pair.strip()
        if pair:
            if ':' in pair:
                part, name = pair.split(':', 1)
                musicians.append((part.strip(), name.strip()))
    return musicians


def parse_needed_instruments(instruments_str: str) -> List[str]:
    """Parse a string of format 'instrument1; instrument2' into list of strings"""
    if not instruments_str or instruments_str.isspace():
        return []

    return [instr.strip() for instr in instruments_str.split(';') if instr.strip()]


def create_ensemble_json(
        song_title: str,
        game: str,
        musicians_needed: List[str],
        current_musicians: List[tuple[str, str]],
        original_track: str,
        other_tracks: Optional[List[str]] = None,
        thumbnail_url: str = "https://png.pngtree.com/png-clipart/20210129/ourmid/pngtree-default-male-avatar-png-image_2811083.jpg",
        user_id: str = "userID"
) -> str:
    """Creates a JSON string for a CarlBot embed representing an ensemble advertisement."""

    current_musicians_text = "\n".join(f"- {part}: {name}" for part, name in current_musicians)
    musicians_needed_text = "\n".join(f"- {part}: **_NEEDED_**" for part in musicians_needed)

    # Only add newline between sections if both exist
    musicians_text = current_musicians_text
    if current_musicians_text and musicians_needed_text:
        musicians_text += "\n"
    musicians_text += musicians_needed_text

    tracks_text = f"\n- Original: {original_track}"
    if other_tracks:
        tracks_text += "\n- " + "\n- ".join(other_tracks)

    embed_dict = {
        "fields": [
            {
                "name": "Musicians",
                "value": musicians_text,
                "inline": False
            },
            {
                "name": "Tracks",
                "value": tracks_text,
                "inline": False
            }
        ],
        "title": f"{song_title} ~ {game}",
        "thumbnail": {
            "url": thumbnail_url
        },
        "author": {
            "name": "Small Ensemble"
        },
        "description": f"Run by @{user_id}",
        "color": 16733952
    }

    return json.dumps(embed_dict, indent=4)


def parse_config_file(file_path: str) -> Dict:
    """Reads and parses a YAML config file."""
    with open(file_path, 'r') as f:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return yaml.safe_load(f)
        else:
            # Assume it's a simple text file with key=value pairs
            config = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
            return config


def process_config(config: Dict) -> Dict:
    """Processes the config dictionary into the format needed for create_ensemble_json."""
    # Convert musicians_needed from string to list if needed
    if isinstance(config.get('musicians_needed'), str):
        config['musicians_needed'] = [x.strip() for x in config['musicians_needed'].split(',')]

    # Convert current_musicians from string to list of tuples if needed
    if isinstance(config.get('current_musicians'), str):
        current_musicians = []
        pairs = config['current_musicians'].split(',')
        for pair in pairs:
            if ':' in pair:
                part, name = pair.split(':')
                current_musicians.append((part.strip(), name.strip()))
        config['current_musicians'] = current_musicians

    # Convert other_tracks from string to list if needed
    if isinstance(config.get('other_tracks'), str):
        config['other_tracks'] = [x.strip() for x in config['other_tracks'].split(',')]

    return config


def process_csv(file_path: str, output_dir: Optional[str] = None) -> None:
    """Process a CSV file and generate JSON for each row"""
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # Create output directory if specified
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        for i, row in enumerate(reader, 1):
            # Process the row data
            config = {
                'song_title': row['Song name'].strip(),
                'game': row['Game'].strip(),
                'original_track': row['OST links'].strip(),
                'user_id': row['Ensemble Lead'].strip() if row['Ensemble Lead'].strip() else "userID",
                'current_musicians': parse_musicians_string(row['Current instruments + members']),
                'musicians_needed': parse_needed_instruments(row['Needed Instruments']),
                'other_tracks': None,  # Could be added as additional column if needed
                'thumbnail_url': None  # Could be added as additional column if needed
            }

            # Generate JSON
            json_str = create_ensemble_json(**config)

            # Determine output
            if output_dir:
                # Create filename from song name (sanitized) and index
                safe_name = "".join(c for c in config['song_title'] if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                filename = f"{i:03d}_{safe_name}.json"
                output_path = Path(output_dir) / filename

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                print(f"Generated JSON for '{config['song_title']}' -> {filename}")
            else:
                print(f"\n--- Ensemble {i}: {config['song_title']} ---")
                print(json_str)
                print("\n" + "=" * 50)


def main():
    parser = argparse.ArgumentParser(description='Generate JSON for CarlBot ensemble embed')

    # Add arguments
    parser.add_argument('-f', '--file', help='Path to config file (YAML or text)')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('-o', '--output-dir', help='Directory to save JSON files (for CSV input)')

    args = parser.parse_args()

    config = {}

    if args.file and args.file.lower().endswith('.csv'):
        process_csv(args.file, args.output_dir)
        return
    elif args.file:
        # Read from file
        config = parse_config_file(args.file)
        config = process_config(config)
    elif args.interactive or not sys.stdin.isatty():
        # Interactive mode or receiving input from pipe
        if args.interactive:
            print("Enter ensemble information:")
            config['song_title'] = input("Song title: ")
            config['game'] = input("Game/Series: ")
            config['musicians_needed'] = input("Musicians needed (comma-separated): ").split(',')

            current_musicians = []
            while True:
                part = input("Current musician part (or enter to finish): ")
                if not part:
                    break
                name = input("Current musician name: ")
                current_musicians.append((part, name))
            config['current_musicians'] = current_musicians

            config['original_track'] = input("Original track link: ")
            other_tracks = input("Other track links (comma-separated, or enter to skip): ")
            if other_tracks:
                config['other_tracks'] = other_tracks.split(',')

            config['user_id'] = input("Discord @ handle: ") or "userID"
            config['thumbnail_url'] = input("Thumbnail URL (or enter for default): ") or None
        else:
            # Reading from pipe
            config = json.load(sys.stdin)
    else:
        parser.print_help()
        return

    # Generate JSON
    json_str = create_ensemble_json(**config)

    # Output
    print(json_str)


if __name__ == "__main__":
    main()