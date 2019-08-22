import QtQuick 2.9
import QtQuick.Window 2.3
import QtQuick.Controls 2.2
import QtQuick.Controls.Universal 2.2
import QtGraphicalEffects 1.0
import QtQuick.Layouts 1.0


Item {
    id: calibHMDitem
    width: mainWindow.width
    height: mainWindow.height
    property alias keyListenerHMD: keyListenerHMD
    property bool recording: false
    property bool stalling: true
    signal moveOn()

    Component.onCompleted: {
        calibHMD.move_on.connect(moveOn);
    }
    onMoveOn: {
        recording = false;
        console.log("move on, dude");
        nextStep();
    }

    function nextStep() {

        if (stalling) {
            //recording, don't do nothing until it's finished
            if (recording) {
                console.log("Wait, recording data...");
                return
            }
            calibHMD.next_target();
            var target = calibControl.target;

            //calibration ended
            if (target[0] === -9 && target[1] === -9) {
                console.log("calibration ended");

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
            nextStep();
        }

        Text {
            width: 271
            height: 54
            anchors.centerIn: parent
            text: qsTr("HMD calibration in progress...\n"+
                       "Press SPACE or DOUBLE_CLICK to\n"+
                       "start recording data from target")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
            font.pointSize: 12
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

