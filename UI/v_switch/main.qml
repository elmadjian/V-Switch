import QtQuick 2.9
import QtQuick.Window 2.3
import QtQuick.Controls 2.2
import QtQuick.Controls.Universal 2.2
import QtGraphicalEffects 1.0
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


    /*
    Right Eye Camera
    ----------------
    */
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
            fillMode: Image.Stretch
            cache: false
            function updateFrame() {
                sceneImage.counter = !sceneImage.counter; //hack to force update
                sceneImage.source = "image://sceneimg/scene" + sceneImage.counter;
            }
        }

    }

    /*
    Left Eye Camera
    ---------------
    */
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

        Image {
            id: leyeImage
            property bool counter: false
            anchors.rightMargin: -10
            anchors.leftMargin: -10
            anchors.bottomMargin: -10
            anchors.topMargin: -10
            source: "image://leyeimg/eye"
            anchors.fill: parent
            fillMode: Image.Stretch
            cache: false
            function updateFrame() {
                leyeImage.counter = !leyeImage.counter; //hack to force update
                leyeImage.source = "image://leyeimg/eye" + leyeImage.counter;
            }
        }
    }

    /*
    Right Eye Camera
    ----------------
    */
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
        Image {
            id: reyeImage
            property bool counter: false
            anchors.rightMargin: -10
            anchors.leftMargin: -10
            anchors.bottomMargin: -10
            anchors.topMargin: -10
            source: "image://reyeimg/eye"
            anchors.fill: parent
            fillMode: Image.Stretch
            cache: false
            function updateFrame() {
                reyeImage.counter = !reyeImage.counter; //hack to force update
                reyeImage.source = "image://reyeimg/eye" + reyeImage.counter;
            }
        }

    }


    /*
    CAM SETTINGS
    ------------
    */
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
                sourceSize.height: 45
                sourceSize.width: 45
                fillMode: Image.PreserveAspectFit
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                source: "../imgs/scene.png"
                z:1

                ColorOverlay {
                    id: sceneOverlayImg
                    anchors.fill: prefSceneImg
                    source: prefSceneImg
                    color: "white"
                    opacity: 0
                }

                MouseArea {
                    id: prefSceneBtn
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    anchors.fill: parent
                    onEntered: {
                        sceneOverlayImg.opacity = 1
                    }
                    onExited: {
                        sceneOverlayImg.opacity = 0
                    }
                    onClicked: {
                        scenePrefDropdown.comboFrameRate.model = sceneCam.fps_list;
                        scenePrefDropdown.comboResolution.model = sceneCam.modes_list;
                        scenePrefDropdown.comboFrameRate.currentIndex = sceneCam.current_fps_index;
                        scenePrefDropdown.comboResolution.currentIndex = sceneCam.current_res_index;
                        scenePrefDropdown.enabled = !scenePrefDropdown.enabled;
                        scenePrefDropdown.opacity = !scenePrefDropdown.opacity;
                        leftEyePrefDropdown.enabled = false;
                        leftEyePrefDropdown.opacity = 0;
                        rightEyePrefDropdown.enabled = false;
                        rightEyePrefDropdown.opacity = 0;
                    }
                }
                Dropdown {
                    id:scenePrefDropdown
                    x: -143
                    y: 49
                    enabled: false;
                    opacity: 0;
                    comboFrameRate.onActivated: {
                        sceneCam.set_mode(comboFrameRate.currentText, comboResolution.currentText);
                        scenePrefDropdown.comboFrameRate.model = sceneCam.fps_list;
                        scenePrefDropdown.comboResolution.model = sceneCam.modes_list;
                        scenePrefDropdown.comboFrameRate.currentIndex = sceneCam.current_fps_index;
                        scenePrefDropdown.comboResolution.currentIndex = sceneCam.current_res_index;
                    }
                    comboResolution.onActivated: {
                        sceneCam.set_mode(comboFrameRate.currentText, comboResolution.currentText);
                        scenePrefDropdown.comboFrameRate.model = sceneCam.fps_list;
                        scenePrefDropdown.comboResolution.model = sceneCam.modes_list;
                        scenePrefDropdown.comboFrameRate.currentIndex = sceneCam.current_fps_index;
                        scenePrefDropdown.comboResolution.currentIndex = sceneCam.current_res_index;
                    }
                }
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
                id: prefLeftEyeImg
                sourceSize.height: 45
                sourceSize.width: 45
                fillMode: Image.PreserveAspectFit
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                source: "../imgs/eye-left.png"
                z:1

                ColorOverlay {
                    id: leftEyeOverlayImg
                    anchors.fill: prefLeftEyeImg
                    source: prefLeftEyeImg
                    color: "white"
                    opacity: 0
                }

                MouseArea {
                    id: prefLeftEyeBtn
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    anchors.fill: parent
                    onEntered: {
                        leftEyeOverlayImg.opacity = 1
                    }
                    onExited: {
                        leftEyeOverlayImg.opacity = 0
                    }
                    onClicked: {
                        leftEyePrefDropdown.comboFrameRate.model = leftEyeCam.fps_list;
                        leftEyePrefDropdown.comboResolution.model = leftEyeCam.modes_list;
                        leftEyePrefDropdown.enabled = !leftEyePrefDropdown.enabled;
                        leftEyePrefDropdown.opacity = !leftEyePrefDropdown.opacity;
                        scenePrefDropdown.enabled = false;
                        scenePrefDropdown.opacity = 0;
                        rightEyePrefDropdown.enabled = false;
                        rightEyePrefDropdown.opacity = 0;
                    }
                }
                Dropdown {
                    id:leftEyePrefDropdown
                    x: -143
                    y: 49
                    enabled: false;
                    opacity: 0;
                    comboFrameRate.onActivated: {
                        console.log("ativei olho esquerdo:" + index);
                    }
                }
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
                id: prefRightEyeImg
                sourceSize.width: 45
                sourceSize.height: 45
                fillMode: Image.PreserveAspectFit
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                source: "../imgs/eye-right.png"
                z:1

                ColorOverlay {
                    id: rightEyeOverlayImg
                    anchors.fill: prefRightEyeImg
                    source: prefRightEyeImg
                    color: "white"
                    opacity: 0
                }

                MouseArea {
                    id: prefRighttEyeBtn
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    anchors.fill: parent
                    onEntered: {
                        rightEyeOverlayImg.opacity = 1
                    }
                    onExited: {
                        rightEyeOverlayImg.opacity = 0
                    }
                    onClicked: {
                        rightEyePrefDropdown.comboFrameRate.model = rightEyeCam.fps_list;
                        rightEyePrefDropdown.comboResolution.model = rightEyeCam.modes_list;
                        rightEyePrefDropdown.enabled = !rightEyePrefDropdown.enabled;
                        rightEyePrefDropdown.opacity = !rightEyePrefDropdown.opacity;
                        scenePrefDropdown.enabled = false;
                        scenePrefDropdown.opacity = 0;
                        leftEyePrefDropdown.enabled = false;
                        leftEyePrefDropdown.opacity = 0;
                    }
                }
                Dropdown {
                    id:rightEyePrefDropdown
                    x: -143
                    y: 49
                    enabled: false;
                    opacity: 0;

                }
            }
        }
    }
}
