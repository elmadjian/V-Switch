const { ipcRenderer } = require('electron');

//STREAMS
//===============
//to receive and update the scene camera frame
ipcRenderer.on("sceneCamFrame", (event, payload) => {
    let sceneFrame = document.querySelector("#sceneCamRenderer");
    let base64Data = btoa(String.fromCharCode.apply(null, payload));
    sceneFrame.src = 'data:image/jpg;base64,' + base64Data;
});

//to receive and update the left eye camera frame
ipcRenderer.on("leftEyeCamFrame", (event, payload) => {
    const leftEyeFrame = document.querySelector("#leftEyeCamRenderer");
    let base64Data = btoa(String.fromCharCode.apply(null, payload));
    leftEyeFrame.src = 'data:image/jpg;base64,' + base64Data;
});

//to receive and update the right eye camera frame
ipcRenderer.on("rightEyeCamFrame", (event, payload) => {
    const rightEyeFrame = document.querySelector("#rightEyeCamRenderer");
    let base64Data = btoa(String.fromCharCode.apply(null, payload));
    rightEyeFrame.src = 'data:image/jpg;base64,' + base64Data;
});



//CAMERA INPUT
//=============
//fetch list of input cameras
ipcRenderer.on("inputCamera", (event, arg) => {
    let elems = document.querySelectorAll('.dropdown-content');
    let data = JSON.parse(JSON.parse(arg));
    for (let i = 0; i < elems.length; i++) {
        while (elems[i].firstChild)
            elems[i].removeChild(elems[i].firstChild);
        for (let j = 0; j < data.length; j++) {
            elems[i].insertAdjacentHTML('beforeend', 
            '<li value="'+data[j][0]+'"><a href="#">'+data[j]+'</a></li>');
        }
    }
    let dropdowns = document.querySelectorAll('.dropdown-content>li');
    for (let i = 0; i < dropdowns.length; i++) {
        dropdowns[i].addEventListener('click', () => {
            const cameraType = dropdowns[i].parentNode.getAttribute("id");
            const value = dropdowns[i].getAttribute("value");
            ipcRenderer.send("changeCamera", cameraType+':'+value);
        });
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



// for (let i = 0; i < dropdowns.length; i++) {
//     console.log("THESE dropdowns: " + dropdowns[i]);
//     for (let j = 0; j < dropdowns[i].children.length; j++) {
//         console.log("ADDING children listeners");
//         dropdowns[i].children[j].addEventListener('click', () => {
//             console.log("criquei em");
//         });
//     }
// }