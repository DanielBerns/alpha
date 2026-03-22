import argparse
import re
import yaml
from pathlib import Path
from datetime import datetime

def process_markdown(input_path: Path, output_dir: Path) -> None:
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    site_title = "Generated Site"
    author = "Unknown Author"

    pages_content = {}
    current_page_title = None
    current_content = []

    # Regex patterns
    author_pattern = re.compile(r'^Author:\s+(.+)', re.IGNORECASE)
    # Matches "## Title" OR "# Day X" (handling the specific formatting error)
    page_header_pattern = re.compile(r'^(?:##|#(?=\s+Day))\s+(.+)', re.IGNORECASE)
    main_title_pattern = re.compile(r'^#\s+(.+)')

    parsed_main_title = False

    for line in lines:
        # 1. Extract the main site title (only the very first "# " line)
        if not parsed_main_title:
            title_match = main_title_pattern.match(line)
            # Ensure we don't accidentally grab the "# Day" formatting error as the main title
            if title_match and not line.lower().startswith("# day"):
                site_title = title_match.group(1).strip()
                parsed_main_title = True
                continue

        # 2. Extract the author
        author_match = author_pattern.match(line)
        if author_match and current_page_title is None:
            author = author_match.group(1).strip()
            continue

        # 3. Detect page boundaries ("## " or the formatting error "# Day")
        page_match = page_header_pattern.match(line)
        if page_match:
            # Save the accumulated content of the previous page
            if current_page_title:
                pages_content[current_page_title] = "".join(current_content)

            current_page_title = page_match.group(1).strip()
            # Normalize the header inside the body to standard markdown level 2
            current_content = [f"## {current_page_title}\n\n"]
            continue

        # 4. Append content to the current page
        if current_page_title:
            current_content.append(line)

    # Save the last parsed page
    if current_page_title and current_content:
        pages_content[current_page_title] = "".join(current_content)

    if not pages_content:
        print("No pages found in the document.")
        return

    # Create the directory structure
    pages_dir = output_dir / "pages"
    resources_img_dir = output_dir / "resources" / "images"
    resources_audio_dir = output_dir / "resources" / "audio"

    for directory in [pages_dir, resources_img_dir, resources_audio_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    # Generate config.yml
    config_data = {
        "site_title": site_title,
        "directories": {
            "pages": "pages",
            "resources": "resources",
            "assets": "assets",
            "templates": "templates"
        }
    }

    with open(output_dir / "config.yml", 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, sort_keys=False)

    # Get the current date for the frontmatter
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Generate individual page files
    for page_title, content in pages_content.items():
        # Clean up the filename so it is filesystem-safe (e.g., "Day 22" -> "day_22.md")
        safe_filename = re.sub(r'[^a-z0-9]+', '_', page_title.lower()).strip('_') + ".md"
        page_path = pages_dir / safe_filename

        # Create YAML Frontmatter with new fields
        frontmatter = f"---\n"
        frontmatter += f"title: \"{page_title}\"\n"
        frontmatter += f"author: \"{author}\"\n"
        frontmatter += f"date: \"{current_date}\"\n"
        frontmatter += f"category: \"Diary\"\n"
        frontmatter += f"---\n\n"

        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter + content)

        print(f"Generated: pages/{safe_filename}")

    print(f"\nProcessing complete! Target structure created at: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Process a single markdown diary/log into an alpha-compatible site structure.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input markdown file (e.g., nicholas_carl.md)")
    parser.add_argument("-o", "--output", required=True, help="Path to the output directory (e.g., ./project_alpha_data)")
    args = parser.parse_args()

    process_markdown(Path(args.input).resolve(), Path(args.output).resolve())

if __name__ == "__main__":
    main()
