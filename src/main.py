import os
import re
import subprocess
import json


def get_commands():
    result = subprocess.run('bash -c "compgen -c"', capture_output=True, text=True, shell=True)
    return result.stdout.splitlines()


def parse_man_page(man_output):
    """Parses the man page output to extract sections like NAME, SYNOPSIS, DESCRIPTION."""
    sections = {
        'name': None,
        'synopsis': None,
        'description': None,
        'options': None,
        'examples': None
    }
    current_section = None

    # Regular expressions to match sections in man pages
    section_headers = {
        'name': re.compile(r'^NAME$', re.IGNORECASE),
        'synopsis': re.compile(r'^SYNOPSIS$', re.IGNORECASE),
        'description': re.compile(r'^DESCRIPTION$', re.IGNORECASE),
        'options': re.compile(r'^OPTIONS$', re.IGNORECASE),
        'examples': re.compile(r'^EXAMPLES$', re.IGNORECASE)
    }

    lines = man_output.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for section, pattern in section_headers.items():
            if pattern.match(line):
                current_section = section
                break
        else:
            if current_section:
                if sections[current_section] is None:
                    sections[current_section] = line
                else:
                    sections[current_section] += ' ' + line

    return sections


def get_man_description(cmd):
    try:
        check_cmd = subprocess.run(['type', cmd], capture_output=True, text=True)
        if check_cmd.returncode != 0:
            return {"command": cmd, "name": None, "synopsis": None, "description": None, "options": None,
                    "examples": None}

        man_process = subprocess.Popen(['man', cmd], stdout=subprocess.PIPE)
        result = subprocess.run(['col', '-b'], stdin=man_process.stdout, capture_output=True, text=True)

        man_process.stdout.close()
        man_process.wait()

        if result.returncode != 0:
            print("Error:", result.stderr)
            return {"command": cmd, "name": None, "synopsis": None, "description": None, "options": None,
                    "examples": None}

        sections = parse_man_page(result.stdout)

        return {
            "command": cmd,
            "name": sections['name'],
            "synopsis": sections['synopsis'],
            "description": sections['description'],
            "options": sections['options'],
            "examples": sections['examples']
        }
    except Exception as e:
        return {"command": cmd, "name": None, "synopsis": None, "description": None, "options": None, "examples": None}


commands = get_commands()

output_file = './output/scrapped.jsonl'
with open(output_file, "w") as file:
    for cmd in commands:
        json.dump(get_man_description(cmd), file)
        file.write('\n')

print(f"Descriptions added to {output_file}")