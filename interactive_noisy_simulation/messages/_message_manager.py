from IPython.display import display, HTML, Javascript
from importlib import resources

# current location
package = __package__
with (resources.files(package) / "styles.css").open("r", encoding="utf8") as file:
    css_code = file.read()
with (resources.files(package) / "scripts.js").open("r", encoding="utf8") as file:
    js_code = file.read()
with (resources.files(package) / "content.html").open("r", encoding="utf8") as file:
    html_code = file.read()

class MessageManager:
    def __init__(self) -> None:
        self.__content_block: str = f"""
            <style>{css_code}</style>
            <script>{js_code}</script>
            {html_code}
        """

    def add_message(self, message: str) -> None:
        message = self.__escape_text(message)
        display(Javascript(f"add_message('{message}');"))

    def create_output(self, heading: str) -> None:
        # content_block = f"""
        # <style>{css_code}</style>
        # <script>{js_code}</script>
        # {html_code}
        # """
        display(HTML(self.__content_block))
        display(Javascript(f"set_heading('{heading}');"))

    def end_output(self):
        self.__unset_id_values()
    
    def __escape_text(self, message: str) -> str:
        return message.replace("'", "&#39;")

    def __unset_id_values(self) -> None:
        display(Javascript(f"unset_id_values();"))
