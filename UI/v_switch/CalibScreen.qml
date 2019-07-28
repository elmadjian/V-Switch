import QtQuick 2.9
import QtQuick.Window 2.3
import QtQuick.Controls 2.2
import QtQuick.Controls.Universal 2.2
import QtGraphicalEffects 1.0
import QtQuick.Layouts 1.0

Window {
    id: calibWindow
    height: 720
    width: 1280
    color: "white"

//    signal pointsList(QVariantList points)
//    Component.onCompleted: calibControl.get_points_list.connect(pointsList);
//    onPointsList: {
//        console.log(points);
//    }

    function nextStep() {
        if (startMessage.opacity == 1) {
            startMessage.opacity = 0;
            calibTarget.visible = true;
            calibTargetOverlay.visible = true;
        }
        if (calibTarget.visible) {

            //move to next position
            if (calibTargetOverlay.opacity == 1) {
                calibControl.next_target();
                var target = calibControl.target;

                //calibration ended
                if (target[0] === -1 && target[1] === -1) {
                    calibTarget.visible = false;
                }
                calibTargetOverlay.opacity = 0;
                calibTarget.x = target[0] * calibWindow.width - calibTarget.width/2;
                calibTarget.y = target[1] * calibWindow.height - calibTarget.height/2;
            }

            //record data
            else {
                calibTargetOverlay.opacity = 1;
            }
        }
    }

    Item {
        id: keyListener
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
        id: mouseListener
        focus: true
        anchors.fill: parent
        onDoubleClicked: {
            nextStep();
        }
    }

    Image {
        visible: false
        id: calibTarget
        source:"../imgs/marker2.png"
        sourceSize.width: calibWindow.width/12
        sourceSize.height: calibWindow.height/6.75
    }

    ColorOverlay {
        visible: false
        id: calibTargetOverlay
        anchors.fill: calibTarget
        source: calibTarget
        color: "red"
        opacity: 1
    }

    Rectangle {
        id: startMessage
        radius: 20
        border.width: 0
        height: 200
        color: "#f0dbc1"
        width: 350
        opacity: 1
        z:2
        anchors.centerIn: parent

        Text {
            width: 271
            height: 54
            anchors.centerIn: parent
            text: qsTr("Press SPACE key or MIDDLE_BTN to start."
                      +" Use the same input to trigger recording"
                      +" for each target.")
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pointSize: 12
        }

    }
}

