function add_message(message) {
    var message_box = document.getElementById("messages");

    var text_element = document.createElement('p');
    text_element.classList.add("messages-text");
    text_element.innerHTML = message;

    message_box.appendChild(text_element);
}

function set_heading(heading) {
    var heading_element = document.getElementById("heading");
    heading_element.innerHTML = heading;
}

function unset_id_values() {
    var ids = ["heading", "messages"];
    for (let i = 0; i < ids.length; i++) {
        element = document.getElementById(ids[i]);
        element.removeAttribute("id");
    }
}
