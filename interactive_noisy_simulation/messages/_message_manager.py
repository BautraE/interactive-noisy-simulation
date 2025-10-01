# Standard library imports:
import json, traceback
from importlib import resources
from typing import Any

#Third party imports:
from IPython.display import display, HTML, Javascript
from pygments import highlight
from pygments.lexers import PythonTracebackLexer
from pygments.formatters import HtmlFormatter

# Local project imports:
from .. import messages
from ..data._data import (
    MESSAGES
)

# Static code that is used for main class method output boxes
with (resources.files(messages) / "styles.css").open("r", encoding="utf8") as file:
    css_code = file.read()

with (resources.files(messages) / "scripts.js").open("r", encoding="utf8") as file:
    js_code = file.read()

with (resources.files(messages) / "content.html").open("r", encoding="utf8") as file:
    html_code = file.read()


class MessageManager:
    
    def __init__(self) -> None:
        """Constructor method """
        self.__content_block: str = f"""
            <style>{css_code}</style>
            <script>{js_code}</script>
            {html_code}
        """


    def add_message(
            self, 
            message: str | dict, 
            highlightables: list[str] = None,
            **placeholder_strings
    ) -> None:
        """Adds a message to the default "Message log" content box

        This method is made to be pretty versatile in terms of being able
        to add and highlight required parts of the given text.
        There are two options for passing the message:
        - As a string in cases, when the message is not stored inside of
            messages.json;
        - As a dictionary in cases, when the message is stored inside of
            messages.json.
        If the message is inside of messages.json, passing highlightables
        is not necessary as they are stored together with the message text
        inside of the file.

        Args:
            message: The message, that will be added to the content box. It can either
                be passed as a string (for more general use) or as a dictionary (when
                the message is stored in the messages.json file).
            highlightables: A list of highlightable string fragments from the current
                message. This argument should only be passed if this method is used for
                more general cases (passing the message as a string instead of a dictionary).
                It can also not be passed, in which case no parts of the message will
                be highlighted.
            **placeholder_strings: Keyword arguments for the str.format() method. They 
                are passed if the message contains placeholders that will be replaced with 
                actual text (in cases, where the messages may be reused for different 
                purposes and situation).
        """
        if isinstance(message, dict):
            message_text = message["text"]
            highlightables = message["highlightables"]
        else: 
            message_text = message

        if placeholder_strings:
            message_text = message_text.format(**placeholder_strings)
            highlightables = [hl.format(**placeholder_strings) for hl in highlightables]

        hl_message = self.__highlight_message(message_text, highlightables)

        display(Javascript(f"addMessage({hl_message});"))


    def add_traceback(self) -> None:
        """Adds simplified traceback message to output block

        The default traceback from Jupyter Notebook files (.ipynb) is
        much more detailed, however, there is no direct way of getting
        the exact traceback that would be printed out by default (at 
        least a method to do so has not yet been discovered or searched
        for).

        The current solution retrieves the traceback string 
        (with self.__get_traceback), formats it to HTML code with CSS 
        styles from the selected formatter style (in this case "lightbulb"), 
        and then passes the HTML and CSS code to a JavaScript function 
        that does the rest.

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
        self.add_message(MESSAGES["exception_occurred"])

        tb_str = self.__get_traceback()

        formatter = HtmlFormatter(full=False, style="lightbulb")
        traceback_html = highlight(tb_str, PythonTracebackLexer(), formatter)
        traceback_css = formatter.get_style_defs()

        escaped_css = json.dumps(traceback_css)
        escaped_html = json.dumps(traceback_html)

        display(Javascript(
            f"addTraceback({escaped_css}, {escaped_html});"
            f"setStatus({0});"
        ))

        self.__unset_id_values()


    def add_qubit_noise_data_container(self) -> None:
        """Adds div container for retrieved qubit noise data

        The created container is initially empty, with the only content
        being the content title "Retrieved qubits:". All the required
        content boxes are added afterwards through other methods.

        This is acomplished with the JavaScript function 
        addQubitNoiseDataContainer().
        """
        display(Javascript(f"addQubitNoiseDataContainer();"))


    def add_qubit_noise_data_content_box(self) -> None:
        """Adds content box for one qubit's noise data

        Each requested qubit will have its own content box for its CSV
        noise data to be inserted into.

        This is acomplished with the JavaScript function 
        addQubitNoiseDataContentBox().
        """
        display(Javascript(f"addQubitNoiseDataContentBox();"))


    def add_qubit_noise_data_row(self, attribute_name: str, value: Any) -> None:
        """Adds row with one qubit's noise data attribute and value
        
        Since every content box for the qubit noise data will contain
        a table, each attribute is being interpreted as a row with two
        columns - the name and value of the current attribute.

        For simplification purposes, as well as due to the information 
        simply being printed out, it is transformed to a string.

        This is acomplished with the JavaScript function 
        addQubitNoiseDataRow(attribute_name, value).
        
        Args:
            attribute_name: Name of the current attribute from the CSV noise data.
            value: Value of the current attribute from the CSV noise data.
        """
        display(Javascript(
            f"addQubitNoiseDataRow("
                f"{json.dumps(str(attribute_name))},"
                f"{json.dumps(str(value))});"
        ))


    def create_output(self, heading: str) -> None:
        """Creates an output box for main class method executions

        This creates the main content container that is displayed after
        executing any main method from the main classes of this module:
        NoiseDataManager, NoiseCreator, etc.

        Args:
            heading: Text for the output box title (main title at the top of
                the container).
        """
        display(HTML(self.__content_block))
        display(Javascript(f"setOutputHeading('{heading}');"))


    def end_output(self) -> None:
        """Marks the end of an output box for some main class method.

        In order for the other output boxes to work as intended, cleanup
        must be done with the current one - mainly by removing ids from the
        currently rendered elements (otherwise there will be issues). The
        helper method __unset_id_values() does this.

        As well as the status of the current output box is modified to mark
        a successful execution.
        """
        display(Javascript(f"setStatus({1});"))
        self.__unset_id_values()


    def generic_content_container(self, heading_text: str) -> None:
        """Modifies the default "Message log" content container for general use

        In some cases, there is no real need for the "Message log", for example,
        printing out informative static content that just simply cannot fail or
        has no steps to the functionality process.

        Args:
            heading_text: Content title text that will replace "Message Log:".
        """
        display(Javascript(
            f"genericContentContainer({json.dumps(heading_text)});"
        ))


    # Private class methods

    def __add_highlight_html(self, text_part: str) -> str:
        """Adds highlight-related HTLM code around the required text
        
        This is a helper method for another helper method: __highlight_message()

        Text fragment highlighting is acomplished by surrounding the highlightable
        text part with a span element that has a CSS class with style related to
        highlighting.

        Args:
            text_part: The text par that needs to be highlighted.
        """
        return f"<span class='highlighted-text'>{text_part}</span>"


    # For some reason json.dumps does not want to work with my custom messages
    # thus this is the solution for escaping text. It might be useful to some day
    # check, which symbols actually cause an issue.
    def __escape_text(self, message: str) -> str:
        """Replaces (escapes) certain symbols of a text so that it is accepted
            in JavaScript.

        This is a helper method that can be used in other class methods.

        Even though json.dumps() already should do the trick, for some reason there
        are things that it does not take care of, leading to issues with adding the
        messages.
        
        Args:
            message: The text that needs to be looked through and contains
                the symbols that should be replaced (escaped).
        """
        escapables = {
            "'": "&#39;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
        }
        for char, replacement in escapables.items():
            message = message.replace(char, replacement)
        return message


    def __get_traceback(self) -> str:
        """Retrieves traceback text for further use by add_traceback method

        This is a helper method for the class method add_traceback().

        In addition to the base functionality, two extra lines are added
        for white space purposes - after first ("Traceback (most recent call last):") 
        and before last line (Exception type and error message).
        """
        tb_str = traceback.format_exc()
        
        tb_lines = tb_str.splitlines()
        tb_lines.insert(1, "")
        tb_lines.insert(len(tb_lines)-1, "")
        return "\n".join(tb_lines)


    def __highlight_message(self, message: str, highlightables: list[str] | None) -> str:
        """Highlights certain parts of a message

        This is a helper method for the class method add_message().

        Both the message text and all highlightable text fragments are
        'escaped'. If highlightables are given, this method goes through
        all of them, retrieves the highlighted variant, replaces the regular
        variant with the highlighted one in the main message, and returns
        the final message back for usage.

        Args:
            message: The main message that may contain fragments needing to be
                highlighted.
            highlightables: A list of text fragments from the main message that 
                must be highlighted.
        """
        esc_message = self.__escape_text(message)
        if highlightables:
            for string in highlightables:
                string = self.__escape_text(string)
                hl_string = self.__add_highlight_html(string)
                esc_message = esc_message.replace(string, hl_string)
        return json.dumps(esc_message)


    def __unset_id_values(self) -> None:
        """Removes id attributes from current output box."""
        display(Javascript(f"unsetIdValues();"))
