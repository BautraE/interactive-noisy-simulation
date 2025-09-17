# Standard library imports:
import json, traceback
from importlib import resources

#Third party imports:
from IPython.display import display, HTML, Javascript
from pygments import highlight
from pygments.lexers import PythonTracebackLexer
from pygments.formatters import HtmlFormatter

# Local project imports:
from .. import data, messages


with (resources.files(messages) / "styles.css").open("r", encoding="utf8") as file:
    css_code = file.read()

with (resources.files(messages) / "scripts.js").open("r", encoding="utf8") as file:
    js_code = file.read()

with (resources.files(messages) / "content.html").open("r", encoding="utf8") as file:
    html_code = file.read()

with (resources.files(data) / "messages.json").open("r", encoding="utf8") as file:
    MESSAGES = json.load(file)


class MessageManager:
    
    def __init__(self) -> None:
        """Constructor method """
        self.__content_block: str = f"""
            <style>{css_code}</style>
            <script>{js_code}</script>
            {html_code}
        """


    def add_traceback(self) -> None:
        """ Adds simplified traceback message to output block

        The default traceback from Jupyter Notebook files (.ipynb) is
        much more detailed, however, there is no direct way of getting
        the exact traceback that would be printed out by default (at 
        least a method to do so has not yet been discovered or searched
        for).

        This is one of two ways of extracting tracebacks that has been
        tried out (with the other one being sys.exc_info() and VerboseTB).
        The current solution was picked as the other one has some complications
        regarding automatic styling with Python Pygments.
        
        Furthermore, regular users of this package might not even need a more
        detailed traceback as error messages are designed to be intuitive
        and self explanatory as to what exactly went wrong.

        Note: 
            When using this method, the functionality of end_output() method
            is automatically applied thus it is not required to write it again.
        """
        self.add_message(f"{MESSAGES["exception_occurred"]}")

        tb_str = self.__get_traceback()

        formatter = HtmlFormatter(full=False, style="lightbulb")
        traceback_html = highlight(tb_str, PythonTracebackLexer(), formatter)
        traceback_css = formatter.get_style_defs()

        escaped_css = json.dumps(traceback_css)
        escaped_html = json.dumps(traceback_html)

        display(Javascript(
            f"add_traceback_block();"
            f"add_traceback({escaped_css}, {escaped_html});"
        ))

        self.end_output()


    def __get_traceback(self) -> str:
        """ Retrieves traceback text for further use by add_traceback method

        In addition to the base functionality, two extra lines are added
        for white space purposes - after first ("Traceback (most recent call last):") 
        and before last line (Exception type and error message).
        """
        tb_str = traceback.format_exc()
        
        tb_lines = tb_str.splitlines()
        tb_lines.insert(1, "")
        tb_lines.insert(len(tb_lines)-1, "")
        return "\n".join(tb_lines)


    def add_message(self, message: str) -> None:
        message = self.__escape_text(message)
        display(Javascript(f"add_message('{message}');"))


    def create_output(self, heading: str) -> None:
        display(HTML(self.__content_block))
        display(Javascript(f"set_heading('{heading}');"))


    def end_output(self) -> None:
        self.__unset_id_values()


    # For some reason json.dumps does not want to work with my custom messages
    def __escape_text(self, message: str) -> str:
        escapables = {
            "'": "&#39;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
        }
        for char, replacement in escapables.items():
            message = message.replace(char, replacement)
        return message


    def __unset_id_values(self) -> None:
        display(Javascript(f"unset_id_values();"))
