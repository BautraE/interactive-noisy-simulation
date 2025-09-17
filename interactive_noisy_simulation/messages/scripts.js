function add_message(message) {
    var text_element = document.createElement('p');
    text_element.classList.add("messages-text");
    text_element.innerHTML = message;

    var message_box = document.getElementById("messages");
    message_box.appendChild(text_element);
}


function add_traceback(traceback_css, traceback_html) {
    // Dynamically add Python pygments generated CSS for tracebacks
    let style = document.createElement("style");
    style.id = "traceback-style";
    style.innerHTML = traceback_css;
    document.head.appendChild(style);

    // Append traceback HTML
    let container = document.getElementById("tracebacks");
    container.insertAdjacentHTML("beforeend", traceback_html);
}


// The created block is very similar to the message log block from content.html
function add_traceback_block() {
    let block_heading = document.createElement("p")
    block_heading.classList.add("block-headings");
    block_heading.innerHTML = "Error log:";

    let traceback_container = document.createElement("div");
    traceback_container.classList.add("content-messages", "traceback-messages");
    traceback_container.id = "tracebacks"
    
    let block_container = document.createElement("div");
    block_container.appendChild(block_heading)
    block_container.appendChild(traceback_container)

    let output_block = document.getElementById("content")
    output_block.appendChild(block_container)
}


function set_heading(heading) {
    var heading_element = document.getElementById("heading");
    heading_element.innerHTML = heading;
}


function unset_id_values() {
    var ids = ["content", "heading", "messages", "tracebacks"];
    for (let i = 0; i < ids.length; i++) {
        element = document.getElementById(ids[i]);
        if (element) {
            element.removeAttribute("id");
        }
    }
}
