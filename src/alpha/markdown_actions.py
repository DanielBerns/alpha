import mimetypes
from pathlib import Path
import re
import yaml
from datetime import datetime

from alpha.git_actions import git_setup_repo
from alpha.static_site_actions import init_project


def markdown_to_spec(input_path: Path, output_dir: Path) -> None:
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        return

    if output_dir.exists():
        # Handle the Git repository conditions BEFORE processing files
        git_setup_repo(output_dir)
    else:
        init_project(output_dir)

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    site_title = "Generated Site"
    author = "Unknown Author"

    pages_content = {}
    current_page_title = None
    current_content = []

    # Regex patterns
    author_pattern = re.compile(r'^Author:\s+(.+)', re.IGNORECASE)
    page_header_pattern = re.compile(r'^(?:##|#(?=\s+Day))\s+(.+)', re.IGNORECASE)
    main_title_pattern = re.compile(r'^#\s+(.+)')

    parsed_main_title = False

    for line in lines:
        if not parsed_main_title:
            title_match = main_title_pattern.match(line)
            if title_match:
                site_title = title_match.group(1).strip()
                parsed_main_title = True
                continue

        author_match = author_pattern.match(line)
        if author_match and current_page_title is None:
            author = author_match.group(1).strip()
            continue

        page_match = page_header_pattern.match(line)
        if page_match:
            if current_page_title:
                pages_content[current_page_title] = "".join(current_content)

            current_page_title = page_match.group(1).strip()
            current_content = [f"## {current_page_title}\n\n"]
            continue

        if current_page_title:
            current_content.append(line)

    if current_page_title and current_content:
        pages_content[current_page_title] = "".join(current_content)

    if not pages_content:
        print("No pages found in the document.", file=sys.stderr)
        return

    # Create the directory structure inside the git repo
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

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Generate individual page files
    for page_title, content in pages_content.items():
        safe_filename = re.sub(r'[^a-z0-9]+', '_', page_title.lower()).strip('_') + ".md"
        page_path = pages_dir / safe_filename

        frontmatter = f"---\n"
        frontmatter += f"title: \"{page_title}\"\n"
        frontmatter += f"author: \"{author}\"\n"
        frontmatter += f"date: \"{current_date}\"\n"
        frontmatter += f"category: \"Diary\"\n"
        frontmatter += f"---\n\n"

        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter + content)

        print(f"Generated: pages/{safe_filename}")

    print(f"\nProcessing complete! Content generated on the appropriate branch in: {output_dir}")


def generate_media_markdown(target_dir: Path, output_file: Path, prefix: str, title: str) -> None:
    if not target_dir.exists() or not target_dir.is_dir():
        print(f"Error: Directory '{target_dir}' does not exist or is not a directory.")
        return

    # Supported extensions
    IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    AUDIO_EXTS = {'.mp3', '.ogg', '.wav', '.m4a', '.flac'}

    media_files = []

    # Scan the target directory
    for file_path in target_dir.iterdir():
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in IMAGE_EXTS:
                media_files.append((file_path.name, 'image'))
            elif ext in AUDIO_EXTS:
                media_files.append((file_path.name, 'audio'))

    if not media_files:
        print(f"No supported image or audio files found in '{target_dir}'.")
        return

    # Sort files alphabetically
    media_files.sort(key=lambda x: x[0])

    # Ensure the output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Make sure prefix ends with a slash if one is provided
    safe_prefix = prefix if not prefix or prefix.endswith('/') else f"{prefix}/"

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write YAML Frontmatter
        f.write(f"---\ntitle: {title}\n---\n\n")
        f.write(f"# {title}\n\n")

        for filename, media_type in media_files:
            media_path = f"{safe_prefix}{filename}"

            # Use the filename as a sub-header for each item
            f.write(f"## {filename}\n\n")

            if media_type == 'image':
                f.write(f"![{filename}]({media_path})\n\n")

            elif media_type == 'audio':
                # Guess mime type so the browser knows how to play it
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    mime_type = "audio/mpeg" # Fallback

                f.write("<audio controls>\n")
                f.write(f'  <source src="{media_path}" type="{mime_type}">\n')
                f.write("  Your browser does not support the audio element.\n")
                f.write("</audio>\n\n")

    print(f"Successfully generated '{output_file}' with {len(media_files)} media embeds.")
