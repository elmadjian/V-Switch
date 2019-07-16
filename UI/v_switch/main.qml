import QtQuick 2.9
import QtQuick.Window 2.3
import QtQuick.Controls 2.2
import QtQuick.Controls.Universal 2.2
import QtGraphicalEffects 1.13
//import CVStuff 1.0
//import CVStuff2 1.0
import QtQuick.Layouts 1.0

Window {
    visible: true
    width: 1050
    height: 650
    color: "#202020"
    title: qsTr("Cadu's Eye Tracker")
    Universal.theme: Universal.Dark
    Universal.accent: Universal.Lime
    // @disable-check M16
    onClosing: {
        console.log("closing window");
        camManager.stop_cameras();
    }

    // @disable-check M204
    Timer {
        id: updater
        interval: 30
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
        x: 30
        y: 140
        width: 660
        height: 490
        topPadding: 32
        rightPadding: 12
        leftPadding: 12
        label: Text {
            id: sceneTitle
            color: "white"
            text: "Scene Camera"
            font.weight: Font.Light
        }

        ComboBox {
            id: sceneBox
            currentIndex: 0
            z: 1
            x: 493
            y: -12
            height: 28
            model: cameraSources
            onActivated:  {
                camManager.set_camera_source(sceneTitle.text, index);
            }
        }

        Image {
            id: sceneImage
            property bool counter: false
            height: 433
            anchors.rightMargin: -10
            anchors.leftMargin: -10
            anchors.bottomMargin: -10
            anchors.topMargin: -10
            anchors.fill: parent
            source: "image://sceneimg/scene"
            fillMode: Image.PreserveAspectFit
            cache: false
            function updateFrame() {
                sceneImage.counter = !sceneImage.counter; //hack to force update
                sceneImage.source = "image://sceneimg/scene" + sceneImage.counter;
            }
        }

    }

    GroupBox {
        id: leftEyeGroup
        x: 710
        y: 140
        width: 315
        height: 238
        label: Text {
            id: leftEyeTitle
            color: "white"
            text: "Left Eye Camera"
            font.weight: Font.Light
        }

        ComboBox {
            id: leftEyeBox
            currentIndex: 1
            z: 1
            x: 141
            y: -12
            height: 28
            model: cameraSources
            onActivated:  {
                camManager.set_camera_source(leftEyeTitle.text, index);
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
                anchors.rightMargin: -10
                anchors.leftMargin: -10
                anchors.bottomMargin: -10
                anchors.topMargin: -10
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
        x: 710
        y: 391
        width: 315
        height: 238
        visible: true
        label: Text {
            id:rightEyeTitle
            color: "white"
            text: "Right Eye Camera"
            font.weight: Font.Light
        }

        ComboBox {
            id: rightEyeBox
            z: 1
            x: 141
            y: -12
            height: 28
            model: cameraSources
            onActivated:  {
                camManager.set_camera_source(rightEyeTitle.text, index);
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
                anchors.rightMargin: -10
                anchors.leftMargin: -10
                anchors.bottomMargin: -10
                anchors.topMargin: -10
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

    GroupBox {
        id: cameraSettings
        x: 710
        y: 16
        width: 315
        height: 110
        label: Text {
            color:"gray"
            text:"Camera Settings"
        }

        RowLayout {
            anchors.rightMargin: 0
            anchors.bottomMargin: 3
            anchors.leftMargin: 0
            anchors.topMargin: -8
            anchors.fill: parent
            spacing: 5

            ColumnLayout {
                y: 0
                width: 65
                height: 60
                Layout.fillHeight: false
                Layout.fillWidth: false
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                Text {
                    id: prefSceneLabel
                    text: qsTr("Scene")
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                }
                Image {
                    id: prefSceneImg
                    sourceSize.height: 50
                    sourceSize.width: 50
                    fillMode: Image.PreserveAspectFit
                    Layout.preferredHeight: 60
                    Layout.preferredWidth: 75
                    source: "../imgs/scene.png"

                    MouseArea {
                        id: prefSceneBtn
                        hoverEnabled: true
                        cursorShape: "PointingHandCursor"
                        anchors.fill: parent

                        onEntered: {

                        }
                    }
                }
                ColorOverlay {
                    anchors.fill: prefSceneImg
                    source: prefSceneImg
                    color: "#ffffff"
                }
            }

            ColumnLayout{
                x: 104
                y: 0
                width: 65
                height: 60
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                Text {
                    id: prefLeftLabel
                    text: qsTr("Left Eye")
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                }
                Image {
                    id: prefLeftCam
                    sourceSize.height: 50
                    sourceSize.width: 50
                    fillMode: Image.PreserveAspectFit
                    Layout.preferredHeight: 60
                    Layout.preferredWidth: 75
                    source: "../imgs/eye-left.png"
                }
            }


            ColumnLayout {
                x: 210
                y: 0
                width: 65
                height: 60
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                Text {
                    id: prefRightLabel
                    text: qsTr("Right Eye")
                    color:"white"
                    horizontalAlignment: Text.AlignHCenter
                }
                Image {
                    id: prefRightCam
                    sourceSize.width: 50
                    sourceSize.height: 50
                    fillMode: Image.PreserveAspectFit
                    Layout.preferredHeight: 60
                    Layout.preferredWidth: 75
                    source: "../imgs/eye-right.png"
                }
            }
        }
    }
}
