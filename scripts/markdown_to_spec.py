import argparse
from pathlib import Path

from alpha.markdown_actions import markdown_to_spec

def main():
    parser = argparse.ArgumentParser(description="Process a single markdown diary/log into an alpha-compatible site structure.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input markdown file (e.g., nicholas_carl.md)")
    parser.add_argument("-o", "--output", required=True, help="Path to the output directory (e.g., ./project_alpha_data)")
    args = parser.parse_args()

    markdown_to_spec(Path(args.input).resolve(), Path(args.output).resolve())

if __name__ == "__main__":
    main()
