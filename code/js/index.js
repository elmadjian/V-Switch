const electron = require('electron');
const { app, BrowserWindow, ipcMain } = electron;
const nng = require('nanomsg');

let sceneCamSubscriber = nng.socket('pull');//zmq.socket('pull');
let leCamSubscriber = nng.socket('pull');
let reCamSubscriber = nng.socket('pull');
let uiSocket = nng.socket('pair');
let window;
let calibscreen;
let backend;


function createWindow() {
    const { spawn } = require('child_process');
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
        sceneCamSubscriber.on('data', (msg) => {
            window.webContents.send("sceneCamFrame", msg);
        });

        //left eye camera handler
        leCamSubscriber.on('data', (msg) => {
            window.webContents.send("leftEyeCamFrame", msg);
        });

        //right eye camera handler
        reCamSubscriber.on('data', (msg) => {
            window.webContents.send("rightEyeCamFrame", msg);
        });

        //7791: scene camera
        //7792: left eye camera
        //7793: right eye camera
        sceneCamSubscriber.connect('ipc:///tmp/camera7791.ipc');
        leCamSubscriber.connect('ipc:///tmp/camera7792.ipc');
        reCamSubscriber.connect('ipc:///tmp/camera7793.ipc');
        uiSocket.connect('ipc:///tmp/ui7798.ipc');
    });
}

//load list of cameras
ipcMain.on("inputCamera", (event, msg) => {
    uiSocket.on('data', (reply) => {
        event.reply("inputCamera", reply);
    });
    uiSocket.send("INPUT_CAMERA");
});

//change camera input
ipcMain.on("changeCamera", (event, msg) => {
    uiSocket.send("CHANGE_CAMERA:" + msg);
});

//start calibration
ipcMain.on("start_calibration", (event, msg) => {
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

//python message parser
uiSocket.on('data', (msg) => {
    let data = msg.toString().split(':');
    switch (data[0]) {
        case 'calib':
            console.log('it is the case: calib:' + data[1]);
            calibscreen.webContents.send("calibrate", 'next');
            break;
        default:
            break;
    }
});

//finish calibration
ipcMain.on("finished_calibration", (event, msg) => {
    if (msg == 'finished') {
        calibscreen.close();
        uiSocket.send("FINISHED_CALIBRATION");
    }

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