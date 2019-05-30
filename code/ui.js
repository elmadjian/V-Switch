const { ipcRenderer } = require('electron');

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

//fetch list of input cameras
ipcRenderer.on("inputCamera", (event, arg) => {
    console.log(arg);
});

//LISTENERS
//=============
document.addEventListener('DOMContentLoaded', () => {
    let elems = document.querySelectorAll('.dropdown-trigger');
    let instances = M.Dropdown.init(elems, 
        {coverTrigger: false,
         onOpenStart: () => {
            ipcRenderer.send("inputCamera");
         }
    });
});