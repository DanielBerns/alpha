import argparse
from pathlib import Path

from alpha.static_site import init_project, build_site

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static site from Markdown and assets.")

    parser.add_argument(
        "--init",
        metavar="DIR",
        help="Initialize a new project in the specified directory"
    )

    parser.add_argument(
        "-c", "--config",
        help="Path to the configuration file (e.g., config.yml) [Required for building]"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output directory where the site and Git repo will be generated [Required for building]"
    )

    args = parser.parse_args()

    if args.init:
        init_project(Path(args.init).resolve())
    else:
        if not args.config or not args.output:
            parser.error("The following arguments are required to build a site: -c/--config and -o/--output")

        config_file_path = Path(args.config).resolve()
        output_dir_path = Path(args.output).resolve()

        build_site(config_file_path, output_dir_path)


if __name__ == "__main__":
    main()
