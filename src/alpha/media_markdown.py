import mimetypes
from pathlib import Path

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Markdown file linking to media files in a directory.")

    parser.add_argument(
        "-d", "--directory",
        required=True,
        help="Path to the directory containing images or audio files"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Path to the output Markdown file (e.g., pages/gallery.md)"
    )
    parser.add_argument(
        "-p", "--prefix",
        default="",
        help="Prefix to prepend to the media paths (e.g., '../resources/images/')"
    )
    parser.add_argument(
        "-t", "--title",
        default="Media Gallery",
        help="Title to use in the Markdown frontmatter and H1 tag"
    )

    args = parser.parse_args()

    generate_media_markdown(
        target_dir=Path(args.directory).resolve(),
        output_file=Path(args.output).resolve(),
        prefix=args.prefix,
        title=args.title
    )
