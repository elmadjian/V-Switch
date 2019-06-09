const electron = require('electron');
const {app, BrowserWindow, ipcMain} = electron;
const zmq = require('zeromq');

let sceneCamSubscriber = zmq.socket('pull');
let leCamSubscriber = zmq.socket('pull');
let reCamSubscriber = zmq.socket('pull');
let uiSocket = zmq.socket('pair');
let window;
let calibscreen;
let backend;


function createWindow() {
    const {spawn} = require('child_process');
    // backend = spawn('python3', ['main.py'], {detached: true});

    window = new BrowserWindow({
        width: 1300, 
        height: 780,
        webPreferences: {
            nodeIntegration: true
        },
    });
    window.loadFile('index.html');

    window.webContents.on('dom-ready', () => {

        //scene camera handler
        sceneCamSubscriber.on('message', (msg) => {
            window.webContents.send("sceneCamFrame", msg);
        });

        //left eye camera handler
        leCamSubscriber.on('message', (msg) => {
            window.webContents.send("leftEyeCamFrame", msg);
        });

        //right eye camera handler
        reCamSubscriber.on('message', (msg) => {
            window.webContents.send("rightEyeCamFrame", msg);
        });

        //7791: scene camera
        //7792: left eye camera
        //7793: right eye camera
        sceneCamSubscriber.connect('tcp://127.0.0.1:7791');
        leCamSubscriber.connect('tcp://127.0.0.1:7792');
        reCamSubscriber.connect('tcp://127.0.0.1:7793');
        uiSocket.connect('tcp://127.0.0.1:7798');
        //console.log("connected to port 7791");
    });
}

//load list of cameras
ipcMain.on("inputCamera", (event, msg) => {
    uiSocket.on('message', (reply) => {
        event.reply("inputCamera", reply);
    });
    uiSocket.send("INPUT_CAMERA");
});

//change camera input
ipcMain.on("changeCamera", (event, msg) => {
    uiSocket.send("CHANGE_CAMERA:" + msg);
});

//perform calibration
ipcMain.on("calibrate", (event, msg) => {
    calibscreen = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    });
    calibscreen.setFullScreen(true);
    calibscreen.loadFile('calibscreen.html');
    uiSocket.send("START_CALIBRATION:" + msg);
});

uiSocket.on('message', (msg) => {
    console.log(msg.toString());
});


app.on('ready', createWindow);
app.on('window-all-closed', () => {
    sceneCamSubscriber.close();
    leCamSubscriber.close();
    reCamSubscriber.close();
    //kill the whole group, not only the spawned process
    // process.kill(-backend.pid); 
    app.quit();
});