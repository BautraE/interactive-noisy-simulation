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
from ..exceptions import DeveloperError
from .helpers.text_styling import style_highlight
from ..data._data import (
    DEV_ERRORS, MESSAGES
)

# Static code that is used for main class method output boxes
with (resources.files(messages) / "static/styles.css").open("r", encoding="utf8") as file:
    css_code = file.read()

with (resources.files(messages) / "scripts/scripts.js").open("r", encoding="utf8") as file:
    js_code = file.read()

with (resources.files(messages) / "static/content.html").open("r", encoding="utf8") as file:
    html_code = file.read()


class MessageManager:
    # =========================================================================
    # Table of Contents for MessageManager
    # =========================================================================
    # 1. Initialization (constructor method).
    # 2. Output box creation / deletion - the beginning and end of any output 
    #       that is rendered in output cells for end-users.
    # 3. Created element ID management - adding IDs to list, whenever a new one
    #       is assigned, and deleting them when necessary.
    # 4. Message log functionality - adding messages to message content box.
    # 5. Tracebacks / Error log - adding traceback-related HTML and CSS to 
    #       output box.
    # 6. Additional content container / box creation.
    # 7. Creating tables and table content.
    # 8. Modification of default message log content container / content box.
    # 9. Other miscelaneous methods - additional methods that provide extra
    #       functionality, but can't be categorized under any other section.
    # =========================================================================


    # =========================================================================
    # 1. Initialization (constructor method).
    # =========================================================================
    
    def __init__(self) -> None:
        """Constructor method."""
        self.__used_ids: list[str] = []
        self.__content_block: str = f"""
            <style>{css_code}</style>
            <script>{js_code}</script>
            {html_code}
        """


    # =========================================================================
    # 2. Output box creation / deletion - the beginning and end of any output 
    #       that is rendered in output cells for end-users.
    # =========================================================================

    def create_output(self, heading: str) -> None:
        """Creates an output box for main class method executions.

        This creates the main content container that is displayed after
        executing any main method from the main classes of this module:
        `NoiseDataManager`, `NoiseCreator`, etc.

        Args:
            heading (str): Text for the output box title (main title at 
                the top of the container).
        """
        self.__remove_element_ids()

        heading = self.__escape_text(heading)
        display(HTML(self.__content_block))
        display(Javascript(f"setOutputHeading('{heading}');"))
        self.__add_element_ids(["output-box", "output-heading", 
                               "message-box-heading", "messages",
                               "status"])


    def end_output(self) -> None:
        """Marks the end of an output box for some main class method.

        In order for the other output boxes to work as intended, cleanup
        must be done with the current one - mainly by removing IDs from 
        the currently rendered elements (otherwise there will be issues). 
        The helper method `__unset_id_values()` does this.

        As well as the status of the current output box is modified to
        mark a successful execution.
        """
        display(Javascript(f"setStatus({1});"))
        self.__remove_element_ids()


    # =========================================================================
    # 3. Created element ID management - adding IDs to list, whenever a new one
    #       is assigned, and deleting them when necessary.
    # =========================================================================

    def __add_element_ids(self, ids: str | list[str]) -> None:
        """Adds used *HTML* element IDs to used IDs list.
        
        The list tracks all currently used IDs so that they all can be
        removed properly afterwards with the help of the mehtod:
        `self.__remove_element_ids()`.

        Args:
            ids (str | list[str]): IDs that will be added to the used
                IDs list.
        """
        # Turns IDs to list for unified processing and code
        # simplification.
        if not isinstance(ids, list):
            ids = [ids]

        self.__check_id_existance(ids, should_exist=False)
        for id in ids:
            self.__used_ids.append(id)


    def __remove_element_ids(self, ids: str | list[str] = None) -> None:
        """Removes IDs from used ID list and *HTML* elements.
        
        Argument values determine removable IDs:
        - `str | list[str]`: will remove the specified IDs.
        - `None`: will remove all IDs from the current used IDs list.

        Args:
            ids (str | list[str]): IDs that will be removed from both the
                used IDs list and respective *HTML* elements.
        """
        # Creates copy of currently used ID list. Without a copy,a reference
        # is used, which will not work properly during list iteration after
        # deletion steps.
        if not ids:
            ids = list(self.__used_ids)
        # Turns IDs to list for unified processing and code
        # simplification.
        elif not isinstance(ids, list):
            ids = [ids]

        for single_id in ids:
            if single_id in self.__used_ids:
                self.__used_ids.remove(single_id)

        self.__unset_id_values(ids)


    def __check_id_existance(
            self, 
            ids: list[str], 
            should_exist: bool
    ) -> None:
        """Validates if ID values are in the used IDs list.
        
        The raised errors indicates an issue during development so that 
        identical ID values don't get used at any point, or so that it is
        made sure that a required parent element exists.

        Args:
            ids (list[str]): list of IDs that will be checked.
            should_exist (bool): should the given IDs currently exist in
                the used IDs list.

        Raises:
            DeveloperError: depends on the argument value of `should_exist`:
                `False`: if at least one given ID value is already part of
                    the used IDs list.
                `True`: if at least one given ID value is not part of the
                    used IDs list.
        """ 
        invalid_ids = [
            id 
            for id in ids 
            if (id in self.__used_ids) != should_exist
        ]
        if invalid_ids:
            error_key = "ids_in_use" if should_exist else "ids_dont_exist"
            raise DeveloperError(DEV_ERRORS[error_key].format(ids=invalid_ids))
            

    def __unset_id_values(self, ids: list[str]) -> None:
        """Removes ID attributes from HTML elements in active output box.
        
        This is done to prepare the next output box to work without any
        issues. The removing process itself is done by the JavaScript 
        function `unsetIdValues()`.

        Args:
            ids (list[str]): list of IDs to remove.
        """
        # List gets made into string because of issues regarding sending
        # complex data structures to JavaScript from Python.
        ids = ",SEPARATOR,".join(ids)

        ids = json.dumps(ids)
        display(Javascript(f"unsetIdValues({ids});"))


    # =========================================================================
    # 4. Message log functionality - adding messages to message content box.
    # =========================================================================

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
            message = self.__highlight_fragments(
                message, highlightable
            )
        
        return json.dumps(message)


    def __highlight_fragments(
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
        `style_highlight()`.
        
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
                message = style_highlight(
                    text=highlightable,
                    message=message,
                    start_position=start,
                    end_position=end
                )
        
        return message


    # =========================================================================
    # 5. Tracebacks / Error log - adding traceback-related HTML and CSS to 
    #       output box.
    # =========================================================================

    def add_traceback(self) -> None:
        """Adds simplified traceback message to output block.

        The default traceback from *Jupyter Notebook* files (`.ipynb`) is
        much more detailed, however, there is no direct way of getting
        the exact traceback that would be printed out by default (at 
        least a method to do so has not yet been discovered or searched
        for).

        The current solution retrieves the traceback string 
        (with `self.__get_traceback`), formats it to HTML code with CSS 
        styles from the selected formatter style (in this case 
        `"lightbulb"`), and then passes the HTML and *CSS* code to a 
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

        tb_str = self.__get_traceback_text()

        formatter = HtmlFormatter(full=False, style="lightbulb")
        traceback_html = highlight(tb_str, PythonTracebackLexer(), formatter)
        traceback_css = formatter.get_style_defs()

        escaped_css = json.dumps(traceback_css)
        escaped_html = json.dumps(traceback_html)

        self.create_content_container(container_id="traceback-container", 
                                      content_heading="Error log:")
        self.create_content_box(box_id="traceback-box",
                                parent_id="traceback-container")

        display(Javascript(
            f"addTraceback({escaped_css}, {escaped_html}, 'traceback-box');"
            f"setStatus({0});"
        ))

        self.__remove_element_ids()


    def __get_traceback_text(self) -> str:
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


    # =========================================================================
    # 6. Additional content container / box creation.
    # =========================================================================

    def create_content_container(
            self, 
            container_id: str, 
            content_heading: str
    ) -> None:
        """Creates and adds new content container to active output box.
        
        Args:
            container_id (str): ID of the new content container element.
            content_heading (str): Content heading text for the new content
                container.
        """
        self.__add_element_ids(container_id)

        container_id = json.dumps(container_id)
        content_heading = json.dumps(f"{content_heading}:")
        display(Javascript(
            f"createContentContainer({container_id}, {content_heading});"))
        

    def create_content_box(
            self, 
            box_id: str, 
            parent_id: str
    ) -> None:
        """Creates and adds new content box for a specific content container.
        
        Args:
            box_id (str): ID of the new content box element.
            parent_id (str): ID of the parent content container element that
                will contain the new content box.
        """
        self.__check_id_existance([parent_id], should_exist=True)
        
        self.__remove_element_ids(box_id)
        self.__add_element_ids(box_id)

        box_id = json.dumps(box_id)
        parent_id = json.dumps(parent_id)
        display(Javascript(
            f"createContentBox({box_id}, {parent_id});"))


    # =========================================================================
    # 7. Creating tables and table content.
    # =========================================================================

    def add_table(self, container_id: str) -> None:
        """Adds table to a specified content box.
        
        Args:
            container_id (str): Id for element that will contain the
                created table.

        This is acomplished with the JavaScript function
        `addTable()`.
        """
        self.__remove_element_ids("table")
        self.__add_element_ids("table")

        container_id = json.dumps(container_id)
        display(Javascript(f"addTable({container_id});"))

    
    def add_table_row(
            self,
            row_content: list[str],
            row_type: str,
            wrap_div: bool = True       
    ) -> None:
        """Adds row to table in the 'messages' content box.
        
        Row content is turned into a single string, separating each
        cell content. This is done, because there are complications with
        sending lists or other data structures to JavaScript from Python 
        with the way that it is being done currently.

        This is acomplished with the JavaScript function
        `addTableRow(row_as_string, row_type)`.

        Args:
            row_content (list[str]): Content for all cells of a row.
            row_type (str): Either `td` for regular data rows or `th` for
                header row.
            wrap_div (bool): Should the cell content be wrapped in div
                elements that limits the maximum width of the table data
                cell (Default: `True`).
        """
        if wrap_div:
            row_content = [
                self.__wrap_div(cell_text) 
                for cell_text in row_content
            ]
        row_as_string = ",SEPARATOR,".join(row_content)
        row_as_string = json.dumps(row_as_string)
        
        display(Javascript(
            f"addTableRow({row_as_string}, '{row_type}');"
        ))


    def __wrap_div(self, text: str) -> str:
        """Adds HTML `<div>` tags around text.

        Workaround used for table cells to limit the automatic width.

        Args:
            text (str): Text that needs HTML `<div>` tags added around it.

        Returns:
            str: Text with added `<div>` tags around it.
        """
        return "<div class='cell-content'>" + text + "</div>"  


    # =========================================================================
    # 8. Modification of default message log content container / content box.
    # =========================================================================

    def modify_content_title(self, heading_text: str) -> None:
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
            f"modifyContentTitle({json.dumps(heading_text)});"
        ))


    # =========================================================================
    # 9. Other miscelaneous methods - additional methods that provide extra
    #       functionality, but can't be categorized under any other section.
    # =========================================================================

    def __escape_text(self, message: str) -> str:
        """Replaces (escapes) certain symbols of a text so that it can
        be correctly interpreted in *JavaScript*.

        This is a helper method that can be used in other class methods.

        This method ensures that text will be displayed with the specific
        symbols included. Without this workaround, they get interpreted as 
        code-related symbols, rather than interpreting them as regular 
        symbols, which is the goal in some situations.
        
        Args:
            message (str): Text that needs to be looked through and 
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



# Message manager object that will be shared across all other main
# manager classes.
message_manager = MessageManager()
