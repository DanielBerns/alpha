import os
import shutil
import subprocess
import argparse
import yaml
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader
from pathlib import Path



from alpha.git_actions import git_setup_repo, git_add_and_commit

def init_project(output_dir: Path):
    print(f"Initializing new project in: {output_dir}")
    git_setup_repo(output_dir)

    # Define the path to the generator's default assets folder
    generator_assets_dir = Path(__file__).parent / "assets"

    if not generator_assets_dir.exists():
        print(f"Error: The generator's default assets folder was not found at {generator_assets_dir}")
        print("Please ensure the 'assets' folder is located next to generator.py.")
        return

    # Create directory structure for the new project
    dirs_to_create = [
        "assets",
        "templates",
        "pages",
        "resources/images",
        "resources/audio"
    ]
    for d in dirs_to_create:
        (output_dir / d).mkdir(parents=True, exist_ok=True)

    # Copy the default files from the generator's assets to the new project
    try:
        shutil.copy(generator_assets_dir / "config.yml", output_dir / "config.yml")
        shutil.copy(generator_assets_dir / "style.css", output_dir / "assets" / "style.css")
        shutil.copy(generator_assets_dir / "base.html", output_dir / "templates" / "base.html")
        shutil.copy(generator_assets_dir / "index.html", output_dir / "templates" / "index.html")
        shutil.copy(generator_assets_dir / "page_1.md", output_dir / "pages" / "page_1.md")
        print("Project initialized successfully! A sample page has been created in 'pages/page_1.md'.")
    except FileNotFoundError as e:
        print(f"Error during initialization: Missing default file. {e}")

    git_add_and_commit(output_dir)

def build_site(config_path: Path, output_dir: Path, alphabetic_sort=False) -> None:
    print(f"Loading configuration from: {config_path}")

    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return

    if not config_path.is_file():
        print(f"Error: Configuration file not found at {config_path}")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    print(f"Building site into: {output_dir}")

    git_setup_repo(output_dir)

    spec_dir = config_path.parent
    dirs = config.get("directories", {})
    spec_resources_dir = spec_dir / dirs.get("resources", "resources")
    spec_assets_dir = spec_dir / dirs.get("assets", "assets")
    spec_templates_dir = spec_dir / dirs.get("templates", "templates")
    spec_pages_dir = spec_dir / dirs.get("pages", "pages")

    output_resources_dir = output_dir / dirs.get("resources", "resources")
    output_assets_dir = output_dir / dirs.get("assets", "assets")
    # output_pages_dir = output_dir / dirs.get("pages", "pages")
    # output_pages_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    output_pages_dir = output_dir

    if spec_resources_dir.exists():
        shutil.copytree(spec_resources_dir, output_resources_dir)
    else:
        print(f"Warning: Resources directory not found at {spec_resources_dir}")

    if spec_assets_dir.exists():
        shutil.copytree(spec_assets_dir, output_assets_dir)
    else:
        print(f"Warning: Assets directory not found at {spec_assets_dir}")

    if not spec_templates_dir.exists():
        print(f"Error: Templates directory not found at {spec_templates_dir}")
        return

    env = Environment(loader=FileSystemLoader(spec_templates_dir))
    page_template = env.get_template("base.html")
    index_template = env.get_template("index.html")

    md = markdown.Markdown(extensions=["fenced_code"])
    pages_metadata = []

    if not spec_pages_dir.exists():
        print(f"Warning: Pages directory not found at {spec_pages_dir}. Skipping markdown processing.")
    else:
        for md_file in spec_pages_dir.glob("*.md"):
            post = frontmatter.load(md_file)
            html_content = md.convert(post.content)

            default_title = md_file.stem.replace("_", " ").title()
            page_title = post.metadata.get("title", default_title)

            final_html = page_template.render(config=config, content=html_content, title=page_title)

            output_filename = f"{md_file.stem}.html"
            output_file = output_pages_dir / output_filename
            with open(output_file, "w", encoding="utf-8") as out_f:
                out_f.write(final_html)
                print(f"Generated: {output_filename}")

            pages_metadata.append({
                "title": page_title,
                "filename": output_filename
            })
        if alphabetic_sort:
            pages_metadata.sort(key=lambda x: x["title"])

        print("\nGenerating index.html...")
        index_html = index_template.render(config=config, pages=pages_metadata)
        with open(output_pages_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)

        git_add_and_commit(output_dir)
