const { ipcRenderer } = require('electron');

//STREAMS
//===============
//to receive and update the scene camera frame
ipcRenderer.on("sceneCamFrame", (event, payload) => {
    const canvas = document.querySelector("#sceneCamRenderer");
    const context = canvas.getContext("2d");
    let base64Data = btoa(String.fromCharCode.apply(null, payload));
    let sceneFrame = new Image();
    sceneFrame.onload = (evt) => {
        context.drawImage(sceneFrame, 0, 0, canvas.width, canvas.height);
    }
    sceneFrame.src = 'data:image/jpg;base64,' + base64Data;
});

//to receive and update the left eye camera frame
ipcRenderer.on("leftEyeCamFrame", (event, payload) => {
    const canvas = document.querySelector("#leftEyeCamRenderer");
    const context = canvas.getContext("2d");
    let base64Data = btoa(String.fromCharCode.apply(null, payload));
    let leftEyeFrame = new Image();
    leftEyeFrame.onload = (evt) => {
        context.drawImage(leftEyeFrame, 0, 0, canvas.width, canvas.height);
    }
    leftEyeFrame.src = 'data:image/jpg;base64,' + base64Data;
});

//to receive and update the right eye camera frame
ipcRenderer.on("rightEyeCamFrame", (event, payload) => {
    const canvas = document.querySelector("#rightEyeCamRenderer");
    const context = canvas.getContext("2d");
    let base64Data = btoa(String.fromCharCode.apply(null, payload));
    let rightEyeFrame = new Image();
    rightEyeFrame.onload = (evt) => {
        context.drawImage(rightEyeFrame, 0, 0, canvas.width, canvas.height);
    }
    rightEyeFrame.src = 'data:image/jpg;base64,' + base64Data;
});



//CAMERA INPUT
//=============
//fetch list of input cameras
ipcRenderer.on("inputCamera", (event, arg) => {
    let elems = document.querySelectorAll('.dropdown-content');
    let data = JSON.parse(JSON.parse(arg));
    let html = "";

    for (let i = 0; i < elems.length; i++) {
        while (elems[i].firstChild)
            elems[i].removeChild(elems[i].firstChild);
        for (let j = 0; j < data.length; j++) {
            let li = document.createElement("li");
            li.appendChild(document.createTextNode(data[j]));
            elems[i].appendChild(li);
        }
    }
});

//Dropdown menu for camera input
document.addEventListener('DOMContentLoaded', () => {
    let elems = document.querySelectorAll('.dropdown-trigger');
    let instances = M.Dropdown.init(elems, 
        {coverTrigger: false,
         onOpenStart: () => {
            ipcRenderer.send("inputCamera");
         }
    });
});