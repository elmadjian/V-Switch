const {app, BrowserWindow, ipcMain} = require('electron');
const zmq = require('zeromq');

const sceneCamSubscriber = zmq.socket('pull');
const leCamSubscriber = zmq.socket('pull');
const reCamSubscriber = zmq.socket('pull');
const uiSocket = zmq.socket('pair');
let window;

function createWindow() {
    const {spawn} = require('child_process');
    const backend = spawn('python', ['main.py']);

    window = new BrowserWindow({
        width: 1200, 
        height: 700,
        webPreferences: {
            nodeIntegration: true
        }
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

        //user input handler
        //IPC-RENDERER -> IPC MAIN -> (zmq) PYTHON THREAD

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

ipcMain.on("inputCamera", (event, msg) => {
    uiSocket.send("INPUT_CAMERA");
    uiSocket.on('message', (reply) => {
        let data = JSON.parse(reply);
        event.reply("inputCamera", data);
    })
});


app.on('ready', createWindow);
app.on('window-all-closed', () => {
    sceneCamSubscriber.close();
    leCamSubscriber.close();
    reCamSubscriber.close();
    app.quit();
});