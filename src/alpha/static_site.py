import os
import shutil
import subprocess
import argparse
import yaml
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def init_project(target_dir: Path):
    print(f"Initializing new project in: {target_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)

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
        (target_dir / d).mkdir(parents=True, exist_ok=True)

    # Copy the default files from the generator's assets to the new project
    try:
        shutil.copy(generator_assets_dir / "config.yml", target_dir / "config.yml")
        shutil.copy(generator_assets_dir / "style.css", target_dir / "assets" / "style.css")
        shutil.copy(generator_assets_dir / "base.html", target_dir / "templates" / "base.html")
        shutil.copy(generator_assets_dir / "index.html", target_dir / "templates" / "index.html")
        shutil.copy(generator_assets_dir / "page_1.md", target_dir / "pages" / "page_1.md")
        print("Project initialized successfully! A sample page has been created in 'pages/page_1.md'.")
    except FileNotFoundError as e:
        print(f"Error during initialization: Missing default file. {e}")


def build_site(config_path: Path, output_dir: Path):
    print(f"Loading configuration from: {config_path}")

    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    base_dir = config_path.parent
    dirs = config.get("directories", {})
    pages_dir = base_dir / dirs.get("pages", "pages")
    resources_dir = base_dir / dirs.get("resources", "resources")
    assets_dir = base_dir / dirs.get("assets", "assets")
    templates_dir = base_dir / dirs.get("templates", "templates")

    print(f"Building site into: {output_dir}")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if resources_dir.exists():
        shutil.copytree(resources_dir, output_dir / "resources")
    else:
        print(f"Warning: Resources directory not found at {resources_dir}")

    css_dir = output_dir / "css"
    css_dir.mkdir()
    if (assets_dir / "style.css").exists():
        shutil.copy(assets_dir / "style.css", css_dir / "style.css")

    if not templates_dir.exists():
        print(f"Error: Templates directory not found at {templates_dir}")
        return

    env = Environment(loader=FileSystemLoader(templates_dir))
    page_template = env.get_template("base.html")
    index_template = env.get_template("index.html")

    md = markdown.Markdown(extensions=["fenced_code"])
    pages_metadata = []

    if not pages_dir.exists():
        print(f"Warning: Pages directory not found at {pages_dir}. Skipping markdown processing.")
    else:
        for md_file in pages_dir.glob("*.md"):
            post = frontmatter.load(md_file)
            html_content = md.convert(post.content)

            default_title = md_file.stem.replace("_", " ").title()
            page_title = post.metadata.get("title", default_title)

            final_html = page_template.render(config=config, content=html_content, title=page_title)

            output_filename = f"{md_file.stem}.html"
            output_file = output_dir / output_filename
            with open(output_file, "w", encoding="utf-8") as out_f:
                out_f.write(final_html)
                print(f"Generated: {output_filename}")

            pages_metadata.append({
                "title": page_title,
                "filename": output_filename
            })

        pages_metadata.sort(key=lambda x: x["title"])

        print("\nGenerating index.html...")
        index_html = index_template.render(config=config, pages=pages_metadata)
        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)

    print("\nInitializing Git repository...")
    try:
        subprocess.run(["git", "init"], cwd=output_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=output_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Build static site"], cwd=output_dir, check=True)
        print("Git repository created and initial commit made successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")

