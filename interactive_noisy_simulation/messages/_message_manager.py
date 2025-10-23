# Standard library imports:
import json, re, traceback
from importlib import resources

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

# Imports only used for type definition:
from typing import Any

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


    def add_generic_table(self) -> None:
        """Adds regular table to the 'messages' content box.
        
        This is acomplished with the JavaScript function
        `addGenericTable()`.
        """
        display(Javascript(f"addGenericTable();"))

    
    def add_generic_table_row(
            self,
            row_content: list[str],
            row_type: str        
    ) -> None:
        """Adds row to table in the 'messages' content box.
        
        Row content is turned into a single string, separating each
        cell content. This is done, because there are complications with
        sending lists or other data structures to JavaScript from Python 
        with the way that it is being done currently.

        This is acomplished with the JavaScript function
        `addGenericTableRow(row_as_string, row_type)`.

        Args:
            row_content (list[str]): Content for all cells of a
                row.
            row_type (str): Either `td` for regular data rows
                or `th` for header row.
        """
        row_content = [
            self.__wrap_div(cell_text) for cell_text in row_content]
        row_as_string = ",SEPARATOR,".join(row_content)
        row_as_string = json.dumps(row_as_string)
        
        display(Javascript(
            f"addGenericTableRow({row_as_string}, '{row_type}');"
        ))  


    def add_message(
            self, 
            message: str | dict, 
            highlightables: list[str] = [],
            **placeholder_strings: str
    ) -> None:
        """Adds a message to the default "Message log" content box.

        This method is made to be pretty versatile in terms of being
        able to add and highlight required parts of the given text.
        There are two options for passing the message:
        - As a string in cases, when the message is not stored inside
            of `messages.json`;
        - As a dictionary in cases, when the message is stored inside
            of `messages.json`.
        If the message is inside of `messages.json`, passing highlightables
        is not necessary as they are stored together with the message 
        text inside of the file.

        Args:
            message (str | dict): The message, that will be added to the 
                content box. It can either be passed as a string (for 
                more general use) or as a dictionary (when the message is
                stored in the `messages.json` file).
            highlightables (list[str]): A list of highlightable string 
                fragments from the current message. This argument should 
                only be passed if this method is used for more general 
                cases (passing the message as a string instead of a 
                dictionary). It can also not be passed, in which case no 
                parts of the message will be highlighted.
            **placeholder_strings (str): Keyword arguments for the 
                `str.format()` method. They are passed if the message 
                contains placeholders that will be replaced with actual 
                text (in cases, where the messages may be reused for 
                different purposes and situation).
        """
        if isinstance(message, dict):
            message_text = message["text"]
            highlightables = message["highlightables"]
        else: 
            message_text = message

        if placeholder_strings:
            message_text = message_text.format(**placeholder_strings)
            highlightables = [
                hl.format(**placeholder_strings) for hl in highlightables]

        message_text = self.__modify_message(message_text, highlightables)

        display(Javascript(f"addMessage({message_text});"))


    def add_traceback(self) -> None:
        """Adds simplified traceback message to output block.

        The default traceback from Jupyter Notebook files (`.ipynb`) is
        much more detailed, however, there is no direct way of getting
        the exact traceback that would be printed out by default (at 
        least a method to do so has not yet been discovered or searched
        for).

        The current solution retrieves the traceback string 
        (with `self.__get_traceback`), formats it to HTML code with CSS 
        styles from the selected formatter style (in this case 
        `"lightbulb"`), and then passes the HTML and CSS code to a 
        JavaScript function that does the rest.

        This is one of two ways of extracting tracebacks that has been
        tried out (with the other one being `sys.exc_info()` and 
        `VerboseTB`). The current solution was picked as the other one 
        has some complications regarding automatic styling with `Python 
        Pygments`.
        
        Furthermore, regular users of this package might not even need 
        a more detailed traceback as error messages are designed to be 
        intuitive and self explanatory as to what exactly went wrong.

        Note: 
            When using this method, the functionality of `end_output()`
            method is automatically applied thus it is not required to 
            write it again.
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
        """Adds div container for retrieved qubit noise data.

        The created container is initially empty, with the only content
        being the content title "Retrieved qubits:". All the required
        content boxes are added afterwards through other methods.

        This is acomplished with the JavaScript function 
        `addQubitNoiseDataContainer()`.
        """
        display(Javascript(f"addQubitNoiseDataContainer();"))


    def add_qubit_noise_data_content_box(self) -> None:
        """Adds content box for one qubit's noise data.

        Each requested qubit will have its own content box for its CSV
        noise data to be inserted into.

        This is acomplished with the JavaScript function 
        `addQubitNoiseDataContentBox()`.
        """
        display(Javascript(f"addQubitNoiseDataContentBox();"))


    def add_qubit_noise_data_row(
            self, 
            attribute_name: str, 
            value: Any
    ) -> None:
        """Adds row with one qubit's noise data attribute and value.
        
        Since every content box for the qubit noise data will contain
        a table, each attribute is being interpreted as a row with two
        columns - the name and value of the current attribute.

        For simplification purposes, as well as due to the information 
        simply being printed out, it is transformed to a string.

        This is acomplished with the JavaScript function 
        `addQubitNoiseDataRow(attribute_name, value)`.
        
        Args:
            attribute_name (str): Name of the current attribute from the 
                CSV noise data.
            value (Any): Value of the current attribute from the CSV 
                noise data.
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
        `NoiseDataManager`, `NoiseCreator`, etc.

        Args:
            heading (str): Text for the output box title (main title at 
                the top of the container).
        """
        heading = self.__escape_text(heading)
        display(HTML(self.__content_block))
        display(Javascript(f"setOutputHeading('{heading}');"))


    def end_output(self) -> None:
        """Marks the end of an output box for some main class method.

        In order for the other output boxes to work as intended, cleanup
        must be done with the current one - mainly by removing ids from 
        the currently rendered elements (otherwise there will be issues). 
        The helper method `__unset_id_values()` does this.

        As well as the status of the current output box is modified to
        mark a successful execution.
        """
        display(Javascript(f"setStatus({1});"))
        self.__unset_id_values()


    def generic_content_container(self, heading_text: str) -> None:
        """Modifies the default "Message log" content container for 
        general use.

        In some cases, there is no real need for the "Message log", for 
        example, printing out informative static content that just simply 
        cannot fail or has no steps to the functionality process.

        Args:
            heading_text (str): Content title text that will replace 
                "Message Log:".
        """
        display(Javascript(
            f"genericContentContainer({json.dumps(heading_text)});"
        ))


    def style_availability_status(self, text:str) -> str:
        """Adds according style to the availability status text.

        In theory, any text can be passed here, but the style will
        only be applied to specific texts.
        
        Args:
            text (str): Text that needs style added to it.

        Returns:
            str: Modified text with added HTML style elements.
        """
        if text == "Available":
            return "<span class='available-instance'>" + text + "</span>"
        else:
            return "<span class='removed-instance'>" + text + "</span>"
        

    def style_file_path(self, text:str) -> str:
        """Adds specific custom style for file path text.

        In theory, any text can be passed here, but the specific
        separator symbols will be highlighted only if they are
        present in the text.
        
        Args:
            text (str): Text that needs style added to it.

        Returns:
            str: Modified text with added HTML style elements.
        """
        replacable = "<span class='path-separators'>\\</span>"
        new_text = re.sub(
            pattern=r'\\', 
            repl=replacable, 
            string=text)
        return "<span class='path-texts'>" + new_text + "</span>"
    
    
    def style_italic(self, text:str) -> str:
        """Adds italic style to the given text.
        
        Args:
            text (str): Text that needs style added to it.

        Returns:
            str: Modified text with added HTML style elements.
        """
        return "<i>" + text + "</i>"


    # Private class methods

    def __add_highlight_tags(
            self, 
            message: str, 
            highlightable: str, 
            start_position: int, 
            end_position: int
    ) -> str:
        """Adds HTML tags to message text with highlight style.

        This is a helper method for the class method
        `__modify_message()`.

        This method takes the current message and adds `span` HTML tags
        around the highlightable message fragment. This is acomplished
        with the start and end position of the highlightable part by
        creating a new message that consists of:
            1. everything before the highlightable part;
            2. the highlightable fragment with added HTML tags;
            3. everything after the highlightable part.

        Args:
            message (str): The current message that needs to be modified.
            highlightable (str): The message fragment that needs to be
                highlighted (surrounded by HTML tags).
            start_position (int): Start position of the highlightable
                fragment inside of the current message.
            end_position (int): End position of the highlightable
                fragment inside of the current message.
        
        Returns:
            str: The modified message with added highlight style for
                the highlightable message fragment (added HTML tags
                around it).
        """
        highlight_element = f"<span class='highlighted-text'>{highlightable}</span>"
        return message[:start_position] + highlight_element + message[end_position:]

    
    # For some reason json.dumps does not want to work with my custom 
    # messages thus this is the solution for escaping text. It might be 
    # useful to some day check, which symbols actually cause an issue.
    def __escape_text(self, message: str) -> str:
        """Replaces (escapes) certain symbols of a text so that it is 
        accepted in JavaScript.

        This is a helper method that can be used in other class methods.

        Even though `json.dumps()` already should do the trick, for some 
        reason there are things that it does not take care of, leading 
        to issues with adding the messages.
        
        Args:
            message (str): The text that needs to be looked through and 
                contains the symbols that should be replaced (escaped).

        Returns:
            str: Modified message text with 'escaped' symbols.
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
        """Retrieves traceback text for further use by `add_traceback()`
        method.

        This is a helper method for the class method `add_traceback()`.

        In addition to the base functionality, two extra lines are added
        for white space purposes - after first ("Traceback (most recent 
        call last):") and before last line (Exception type and error 
        message).

        Returns:
            str: Text of the retrieved traceback that will be formatted
                and displayed to the user.
        """
        tb_str = traceback.format_exc()
        
        tb_lines = tb_str.splitlines()
        tb_lines.insert(1, "")
        tb_lines.insert(len(tb_lines)-1, "")
        return "\n".join(tb_lines)


    def __highlight_message(
            self,
            message: str, 
            highlightable: str, 
    ) -> str:
        """Adds highlighting style to each highlightable in message.

        This is a helper method for the method `__modify_message()`.

        The simple `str.replace()` function did not work for this, because
        it would highlight fragments that are a part of a word, which 
        is not the goal - highlighting specific words, phrases, elements 
        from messages.
        
        Instead of replacing the highlightable with a variant of it with
        added HTML tags added, the tags are 'appended' to the text.
        This functionality is implemented in the class method 
        `__add_highlight_tags()`.
        
        The appending process works in reverse by starting with 
        highlightable instances that are located closer to the end of the 
        message. This is done so that position numbers don't get messed 
        up after something gets highlighted, because the modified message 
        text replaces the current oneall the time.
        
        Validation if the matchet message fragment is a valid highlightable
        (a specific word, phrase, element) is achieved with certain 
        acceptable symbols before and after the matched fragment. If both
        are acceptable, the fragment will be highlighted.

        Args:
            message (str): Text that contains highlightables that need 
                highlight related styles applied to them.
            highlightable (str): The current highlightable fragment that 
                will be located in the current message and have highlighting 
                style applied to it.

        Returns:
            str: Message text with all valid cases of a highlightable 
                highlighted (with added `<span>` elements that give the 
                required highlight style)
        """
        escaped_highlightable = re.escape(highlightable)
        
        # All found matches for the current highlightable
        matches = re.finditer(rf'{escaped_highlightable}', message)
        # Iterates through matches in reverse order. The reverse order
        # is determined by the key function, which will sort by the start
        # position of each found match.
        for match in sorted(matches, key=lambda m: m.start(), reverse=True):

            start, end = match.start(), match.end()
            
            before = message[start - 1] if start > 0 else ''
            after = message[end] if end < len(message) else ''
            
            is_prev_allowed = False
            is_next_allowed = False
            if before in ["", " "]:
                is_prev_allowed = True
            if after in ["", " ", "!", "?", ".", ",", ":"]:
                is_next_allowed = True

            if is_prev_allowed and is_next_allowed:
                message = self.__add_highlight_tags(
                    message,
                    highlightable,
                    start_position=start,
                    end_position=end
                )
        
        return message

    
    def __modify_message(
            self, 
            message: str, 
            highlightables: list[str]
    ) -> str:
        """Highlights certain parts of a message.

        This is a helper method for the class method `add_message()`.

        Both the message text and all highlightable text fragments are
        'escaped'. 
        If highlightables are given, this method goes through all of 
        them, modifies the current message text by adding the required
        highlighting style for each highlightable in it, and returns 
        the final message back for `display`.

        Args:
            message (str): The main message that may contain fragments 
                needing to be highlighted.
            highlightables (list[str]): A list of text fragments from 
                the main message that must be highlighted.

        Returns:
            str: Modified message that is ready to be displayed.
        """
        message = self.__escape_text(message)
        
        for highlightable in highlightables:
            highlightable = self.__escape_text(highlightable) 
            message = self.__highlight_message(
                message, highlightable
            )
        
        return json.dumps(message)

    
    def __unset_id_values(self) -> None:
        """Removes id attributes from current output box.
        
        This is done to prepare the next output box to work without any
        issues.
        """
        display(Javascript(f"unsetIdValues();"))


    def __wrap_div(self, text: str) -> str:
        """Adds HTML `<div>` tags around text.

        Workaround used for table cells to limit the automatic width.

        Args:
            text (str): Text that will have HTML `<div>` tags added around it.

        Returns:
            str: Text with added `<div>` tags around it.
        """
        return "<div class='cell-content'>" + text + "</div>"
