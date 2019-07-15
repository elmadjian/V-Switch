import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.5
import QtQuick.Controls.Universal 2.3
//import CVStuff 1.0
//import CVStuff2 1.0

Window {
    visible: true
    width: 1000
    height: 600
    color: "#202020"
    title: qsTr("Cadu's Eye Tracker")
    Universal.theme: Universal.Dark
    Universal.accent: Universal.Lime

    Timer {
        id: updater
        interval: 60
        running: true
        repeat: true
        onTriggered: {
            sceneImage.updateFrame();
            leyeImage.updateFrame();
            reyeImage.updateFrame();
        }
    }

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
               camManager.set_camera_source(sceneGroup.title, index);
            }

        }
        Canvas {
            id: sceneCam
            z: 0
            x: -12
            y: 22
            width: 645
            height: 430
            anchors.fill: parent
            renderStrategy: Canvas.Threaded
            Image {
                id: sceneImage
                property bool counter: false
                source: "image://sceneimg/scene"
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                cache: false
                function updateFrame() {
                    sceneImage.counter = !sceneImage.counter; //hack to force update
                    sceneImage.source = "image://sceneimg/scene" + sceneImage.counter;
                }
            }
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
                camManager.set_camera_source(leftEyeGroup.title, index);
            }
        }

        Canvas {
            id: leftEyeCam
            z: 0
            x: -12
            y: 22
            width: 293
            height: 191
            anchors.fill: parent
            renderStrategy: Canvas.Threaded
            Image {
                id: leyeImage
                property bool counter: false
                source: "image://leyeimg/eye"
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                cache: false
                function updateFrame() {
                    leyeImage.counter = !leyeImage.counter; //hack to force update
                    leyeImage.source = "image://leyeimg/eye" + leyeImage.counter;
                }
            }
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
                camManager.set_camera_source(rightEyeGroup.title, index);
            }
        }

        Canvas {
            id: rightEyeCam
            z: 0
            x: -12
            y: 22
            width: 293
            height: 191
            anchors.fill: parent
            renderStrategy: Canvas.Threaded
            Image {
                id: reyeImage
                property bool counter: false
                source: "image://reyeimg/eye"
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                cache: false
                function updateFrame() {
                    reyeImage.counter = !reyeImage.counter; //hack to force update
                    reyeImage.source = "image://reyeimg/eye" + reyeImage.counter;
                }
            }
        }
    }

}
