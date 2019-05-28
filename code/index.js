const {app, BrowserWindow} = require('electron');

function createWindow() {
    const {spawn} = require('child_process');
    const backend = spawn('python', ['main.py']);

    window = new BrowserWindow({width: 800, height: 600});
    window.loadFile('index.html');

    var zerorpc = require('zerorpc');
    var client = new zerorpc.Client();
    client.connect("tcp://127.0.0.1:4242");
    client.invoke("printSomething", function(error, res, more) {
        console.log(res);
    });
}

app.on('ready', createWindow);
app.on('window-all-closed', () => {
    app.quit()
});