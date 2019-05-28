const { ipcRenderer } = require('electron');

//to receive and update the scene camera frame
ipcRenderer.on("sceneCamFrame", (event, payload) => {
    //let placeholder = document.querySelector("#placeholder");
    //placeholder.innerHTML = message;
});

//to receive and update the left eye camera frame
ipcRenderer.on("leftEyeCamFrame", (event, payload) => {

});

//to receive and update the right eye camera frame
ipcRenderer.on("rightEyeCamFrame", (event, payload) => {
    
});