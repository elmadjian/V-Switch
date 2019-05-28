const {app, BrowserWindow} = require('electron');

let window;

function createWindow() {
    const {spawn} = require('child_process');
    const backend = spawn('python', ['main.py']);

    window = new BrowserWindow({
        width: 1000, 
        height: 700
    });
    window.loadFile('index.html');

    window.webContents.on('dom-ready', () => {
        var zerorpc = require('zerorpc');
        var client = new zerorpc.Client();
        client.connect("tcp://127.0.0.1:4242");
        client.invoke("printSomething", function(error, res, more) {
            window.webContents.send("texto", res);

        });
    });
    
}

app.on('ready', createWindow);
app.on('window-all-closed', () => {
    app.quit()
});