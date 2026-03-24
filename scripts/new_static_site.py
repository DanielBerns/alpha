import argparse
import re
import yaml
import subprocess
import sys
from pathlib import Path
from datetime import datetime




def main():
    parser = argparse.ArgumentParser(description="Process a markdown diary into an alpha-compatible site and manage its Git state.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input markdown file (e.g., nicholas_carl.md)")
    parser.add_argument("-o", "--output", required=True, help="Path to the output directory (e.g., ./project_alpha_data)")
    args = parser.parse_args()

    process_markdown(Path(args.input).resolve(), Path(args.output).resolve())

if __name__ == "__main__":
    main()
