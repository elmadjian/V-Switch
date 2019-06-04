let img;
let width;
let height;
let pos;
let count = 1;

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

    //controlling target movement
    window.addEventListener("click", () => {
        if (count >= pos.length) {
            console.log("completed");
            return;
        }
        let p = pos[count];
        let top = String(Math.round(p[0] * height)) + "px";
        let left = String(Math.round(p[1] * width)) + "px";
        count++;
        img.style.top = top;
        img.style.left = left;
    });

    // let startButton = document.querySelector('#start');
    // startButton.addEventListener("click", () => {
    //     startButton.style.display = "none";
    //     img.style.display = "block";
    // });

};



