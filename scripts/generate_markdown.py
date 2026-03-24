import argparse
from pathlib import Path

from alpha.markdown_actions import generate_markdown_gallery


def main() -> None:
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

    generate_markdown_gallery(
        target_dir=Path(args.directory).resolve(),
        output_file=Path(args.output).resolve(),
        prefix=args.prefix,
        title=args.title
    )

if __name__ == "__main__":
    main()
