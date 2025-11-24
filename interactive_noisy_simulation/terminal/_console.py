# Third party imports:
from rich.console import Console
from rich_argparse import RichHelpFormatter
from rich.style import Style
from rich.theme import Theme

# Theme that is used by the console. Defines tags that
# can be used in the messages.json file.
theme = Theme({
    "command": Style(color="#00FFFF", bold=False),
    "failure": "#FF8A8A",
    "highlight": Style(color="#FFD173", bold=False),
    "name": "italic",
    "success": "#37FF8D"
})

# Console used for printing messages in terminal:
console = Console(theme=theme, style="#97a6d4")

# Custom formatter for the -h | --help command:
__custom_formatter_styles = {
    "argparse.args": "#00FFFF",
    'argparse.groups': "#FFD173",
    "argparse.text": "#97a6d4",
    'argparse.help': "#97a6d4",
    'argparse.prog': "#40A5F3"
}
RichHelpFormatter.styles.update(__custom_formatter_styles)
