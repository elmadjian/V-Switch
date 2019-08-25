import QtQuick 2.9
import QtQuick.Window 2.3
import QtQuick.Controls 2.2
import QtQuick.Controls.Universal 2.2
import QtGraphicalEffects 1.0
import QtQuick.Layouts 1.0


Item {
    id: calibHMDitem
    visible: false
    width: mainWindow.width
    height: mainWindow.height
    property alias keyListenerHMD: keyListenerHMD
    property bool recording: false
    property bool stalling: false
    signal moveOn()
    signal connStatus(var connectionStatus)

    Component.onCompleted: {
        calibHMD.move_on.connect(moveOn);
        calibHMD.conn_status.connect(connStatus);
    }

    onMoveOn: {
        recording = false;
        nextStep();
    }

    onConnStatus: {
        if (connectionStatus)
            calibHMDText.state = "success";
        else {
            calibHMDText.state = "failed";
        }
    }

    function reset() {
        calibHMDitem.visible = false;
        calibHMDText.state = "connecting";
    }

    function nextStep() {
        if (calibHMDText.state == "success") {
            calibHMDText.state = "calibrating";
            stalling = true;
        }

        if (stalling) {
            //recording, don't do nothing until it's finished
            if (recording) {
                console.log("Wait, recording data...");
                return
            }
            calibHMD.next_target();
            var target = calibHMD.target;

            //calibration ended
            if (target[0] === -9 && target[1] === -9) {
                console.log("calibration ended");
                calibHMD.perform_estimation();
                reset();
            }
            stalling = false;

        }
        //record data
        else {
            stalling = true;
            recording = true;
            var freq_leye = leftEyeCam.current_fps;
            var freq_reye = rightEyeCam.current_fps;
            var max_freq  = Math.max(freq_leye, freq_reye);
            var min_freq  = Math.min(freq_leye, freq_reye);
            calibHMD.collect_data(min_freq, max_freq);
        }
    }

    Rectangle {
        id: calibHMDmode
        width: parent.width
        height: parent.height
        anchors.fill: parent
        opacity: 0.5
        color: "black"
        z:3
    }

    Rectangle {
        id: calibHMDmessage
        radius: 20
        border.width: 0
        height: 200
        color: "#f0dbc1"
        width: 350
        opacity: 1
        z:4
        anchors.centerIn: parent
        Component.onCompleted: {
            calibHMDText.state = "connecting";
        }

        Text {
            id: calibHMDText
            width: 271
            height: 54
            anchors.centerIn: parent
            text: qsTr("")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
            font.pointSize: 12

            onVisibleChanged: {
                if (visible) {
                    console.log("connecting");
                    calibHMD.connect();
                }
            }

            Button {
                id: closeHMDbtn
                x: 86
                y: 62
                visible: false
                text: "OK"
                onClicked: {
                    calibHMDitem.visible = false;
                    closeHMDbtn.visible = false;
                    calibHMDText.state = "connecting";
                }
            }

            states: [
                State {
                    name: "connecting"
                    PropertyChanges {
                        target: calibHMDText
                        text: qsTr("Searching for HMD...")
                    }
                },
                State {
                    name: "failed"
                    PropertyChanges {
                        target: calibHMDText
                        text: qsTr("Could not find an HMD with current network settings")
                    }
                    PropertyChanges {
                        target: closeHMDbtn
                        visible: true
                    }
                },
                State {
                    name: "success"
                    PropertyChanges {
                        target: calibHMDText
                        text: qsTr("HMD found!\n"+
                                   "Press SPACE or DOUBLE_CLICK to "+
                                   "start recording data from target")
                    }
                },
                State {
                    name: "calibrating"
                    PropertyChanges {
                        target: calibHMDText
                        text: qsTr("Calibration in progress...")

                    }
                }
            ]
        }
    }
    Item {
        id: keyListenerHMD
        focus: true
        anchors.fill: parent
        Keys.onPressed: {
            if (event.key === Qt.Key_Space) {
                event.accepted = true;
                nextStep();
            }
        }
    }
    MouseArea {
        id: mouseListenerHMD
        focus: true
        anchors.fill: parent
        onDoubleClicked: {
            nextStep();
        }
    }
}

//Window {
//    id: calibWindow
//    height: 720
//    width: 1280
//    color: "white"
//    property var recording: false
//    property var counter: 0

//    signal moveOn()

//    // @disable-check M16
//    onClosing: {
//        console.log("closing calib window");
//        markerCenter.opacity = 0;
//        calibTarget.visible = false;
//        calibTargetOverlay.opacity = 0;
//        reset();
//    }

//    Component.onCompleted: {
//        calibControl.move_on.connect(moveOn);
//    }
//    onMoveOn: {
//        recording = false;
//        nextStep();
//    }

//    function reset() {
//        calibWindow.visible = false;
//        estimationMessage.opacity = 0;
//        startMessage.opacity = 1;
//    }


//    Rectangle {
//        id: estimationMessage
//        radius: 20
//        border.width: 0
//        height: 200
//        color: "#f0dbc1"
//        width: 350
//        opacity: 0
//        z:2
//        anchors.centerIn: parent

//        Text {
//            width: 271
//            height: 54
//            anchors.centerIn: parent
//            text: qsTr("Performing gaze estimation. Please wait.")
//            horizontalAlignment: Text.AlignHCenter
//            wrapMode: Text.WordWrap
//            font.pointSize: 12
//        }
//    }
//}

