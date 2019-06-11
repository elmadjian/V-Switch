const { ipcRenderer } = require('electron');

let img;
let width;
let height;
let pos;
let count = 1;

//move to next target on screen
function moveNext() {
    if (count >= pos.length) {
        console.log("completed");
        ipcRenderer.send('finished_calibration', 'finished');
        return;
    }
    let p = pos[count];
    let top = String(Math.round(p[0] * height)) + "px";
    let left = String(Math.round(p[1] * width)) + "px";
    count++;
    img.style.top = top;
    img.style.left = left;
    console.log("moving to next target");
}

window.onload = () => {
    img = document.querySelector("img");
    pos = [
        [0.05, 0.05], [0.05, 1 / 3], [0.05, 2 / 3], [0.05, 0.95],
        [0.5, 0.05], [0.5, 1 / 3], [0.5, 2 / 3], [0.5, 0.95],
        [0.95, 0.05], [0.95, 1 / 3], [0.95, 2 / 3], [0.95, 0.95]
    ];
    width = window.innerWidth - img.width;
    height = window.innerHeight - img.height;
    img.style.top = String(Math.round(pos[0][0] * height)) + "px";
    img.style.left = String(Math.round(pos[0][1] * width)) + "px";

    //controlling target movement with click
    window.addEventListener("click", moveNext);

};

//controlling target movement with data amount
ipcRenderer.on("calibrate", (event, arg) => {
    switch (arg) {
        case 'next':
            moveNext();
            break;
        default:
            break;
    }
});



