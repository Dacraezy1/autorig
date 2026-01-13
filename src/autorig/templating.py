from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    def __init__(self, search_path: Path):
        self.env = Environment(loader=FileSystemLoader(str(search_path)))

    def render(self, template_name: str, context: Dict[str, Any], output_path: Path):
        template = self.env.get_template(template_name)
        content = template.render(**context)
        output_path.write_text(content)

    def render_string(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
