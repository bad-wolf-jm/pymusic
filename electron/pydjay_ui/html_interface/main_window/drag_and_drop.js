var accordion_open_promise = undefined

function open_accordion(evt) {
    let panel = evt.target.nextElementSibling;
    accordion_open_promise = setTimeout(() => {
        evt.target.classList.toggle("active");
        panel.style.maxHeight = panel.scrollHeight + "px";
        //clearInterval(accordion_open_promise)
    }, 1000)
}

function cancel_open_accordion() {
    clearTimeout(accordion_open_promise)
}

var droppable = document.querySelectorAll('.open-on-drag-over');
[].forEach.call(droppable, (col) => {
    //console.log(col)
    col.addEventListener('dragenter', open_accordion, false);
    col.addEventListener('dragleave', cancel_open_accordion, false);
});
