import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.5
import QtQuick.Controls.Universal 2.3
import CVStuff 1.0
//import CVStuff2 1.0

Window {
    visible: true
    width: 1000
    height: 600
    color: "#202020"
    title: qsTr("Cadu's Eye Tracker")
    Universal.theme: Universal.Dark
    Universal.accent: Universal.Lime

//    Timer {
//        id: updater
//        interval: 50
//        running: true
//        repeat: true
//        onTriggered: {
//            sceneCam.updateFrame();
//            leftEyeCam.updateFrame();
//        }
//    }

    GroupBox {
        id: sceneGroup
        x: 24
        y: 116
        width: 645
        height: 464
        font.weight: Font.Light
        title: qsTr("Scene Camera")

        ComboBox {
            id: sceneBox
            currentIndex: 0
            z: 1
            x: 493
            y: -12
            height: 28
            model: cameraSources
            onActivated:  {
               sceneCam.set_camera_source(index);
            }

        }
        SceneCamera {
            id: sceneCam
            z: 0
            x: -12
            y: 22
            width: 645
            height: 430
            anchors.fill: parent
//            function updateFrame() {
//                sceneCam.set_image(sceneCamCV.scene_image);
//            }
        }
    }

    GroupBox {
        id: leftEyeGroup
        x: 686
        y: 116
        width: 293
        height: 225
        title: qsTr("Left Eye")

        ComboBox {
            id: leftEyeBox
            currentIndex: 1
            z: 1
            x: 141
            y: -12
            height: 28
            model: cameraSources
            onActivated:  {
               leftEyeCam.set_camera_source(index);
            }
        }

        LeftEyeCamera {
            id: leftEyeCam
            z: 0
            x: -12
            y: 22
            width: 293
            height: 191
//            function updateFrame() {
//                leftEyeCam.set_image(leftEyeCamCV.eye_image);
//            }
        }
    }

    GroupBox {
        id: rightEyeGroup
        x: 686
        y: 355
        width: 293
        height: 225
        visible: true
        title: qsTr("Right Eye")

        ComboBox {
            id: rightEyeBox
            z: 1
            x: 141
            y: -12
            height: 28
            model: cameraSources
            onActivated:  {
               rightEyeCam.set_camera_source(index);
            }
        }

        Canvas {
            id: rightEyeCam
            z: 0
            x: -12
            y: 22
            width: 293
            height: 191
        }
    }

}
