import json
import argparse
import sys
from typing import List, Optional, Dict
import yaml  # For reading YAML config files


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

    musicians_needed_text = "\n".join(f"- {part}" for part in musicians_needed)
    current_musicians_text = "\n".join(f"- {part} {name}" for part, name in current_musicians)

    tracks_text = f"\n- Original: {original_track}"
    if other_tracks:
        tracks_text += "\n- " + "\n- ".join(other_tracks)

    embed_dict = {
        "fields": [
            {
                "name": "Musicians Needed",
                "value": musicians_needed_text,
                "inline": False
            },
            {
                "name": "Current Musicians",
                "value": current_musicians_text,
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
        "description": f"Run by <@!{user_id}>",
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


def main():
    parser = argparse.ArgumentParser(description='Generate JSON for CarlBot ensemble embed')

    # Add arguments
    parser.add_argument('-f', '--file', help='Path to config file (YAML or text)')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('-c', '--compact', action='store_true', help='Output compact JSON')

    args = parser.parse_args()

    config = {}

    if args.file:
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

            config['user_id'] = input("Discord user ID (or enter for default): ") or "userID"
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
    if args.compact:
        print(json.dumps(json.loads(json_str), separators=(',', ':')))
    else:
        print(json_str)


if __name__ == "__main__":
    main()