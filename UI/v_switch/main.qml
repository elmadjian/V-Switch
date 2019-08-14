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
    title: qsTr("V-Switch Eye Tracker")
    Universal.theme: Universal.Dark
    Universal.accent: Universal.Lime
    // @disable-check M16
    onClosing: {
        console.log("closing window");
        camManager.stop_cameras();
    }


    /*
    Scene Camera
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
                activate_config(sceneDisabledOverlay, prefSceneImg);
                enable_calibration();
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
            source: "../imgs/novideo.png"
            fillMode: Image.Stretch
            cache: false

            signal updateImage()
            Component.onCompleted: sceneCam.update_image.connect(updateImage);

            Connections {
                target: sceneImage
                onUpdateImage: {
                    sceneImage.counter = !sceneImage.counter; //hack to force update
                    sceneImage.source = "image://sceneimg/scene" + sceneImage.counter;
                }
            }
            //Draw gaze prediction on top of the image !!!
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
                activate_config(leftEyeDisabledOverlay, prefLeftEyeImg);
                enable_calibration();
            }
        }

        Image {
            id: leyeImage
            property bool counter: false
            anchors.rightMargin: -10
            anchors.leftMargin: -10
            anchors.bottomMargin: -10
            anchors.topMargin: -10
            source: "../imgs/novideo.png"
            anchors.fill: parent
            fillMode: Image.Stretch
            cache: false

            signal updateImage()
            Component.onCompleted: leftEyeCam.update_image.connect(updateImage);

            Connections {
                target: leyeImage
                onUpdateImage: {
                    leyeImage.counter = !leyeImage.counter; //hack to force update
                    leyeImage.source = "image://leyeimg/eye" + leyeImage.counter;
                }
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
                activate_config(rightEyeDisabledOverlay, prefRightEyeImg);
                enable_calibration();
            }
        }
        Image {
            id: reyeImage
            property bool counter: false
            anchors.rightMargin: -10
            anchors.leftMargin: -10
            anchors.bottomMargin: -10
            anchors.topMargin: -10
            source: "../imgs/novideo.png"
            anchors.fill: parent
            fillMode: Image.Stretch
            cache: false

            signal updateImage()
            Component.onCompleted: rightEyeCam.update_image.connect(updateImage);

            Connections {
                target: reyeImage
                onUpdateImage: {
                    reyeImage.counter = !reyeImage.counter; //hack to force update
                    reyeImage.source = "image://reyeimg/eye" + reyeImage.counter;
                }
            }
        }

    }


    //Helper functions
    //----------------
    function update_comboboxes(uid, camType) {
        uid.comboFrameRate.model = camType.fps_list;
        uid.comboResolution.model = camType.modes_list;
        uid.comboFrameRate.currentIndex = camType.current_fps_index;
        uid.comboResolution.currentIndex = camType.current_res_index;
    }

    function activate_dropdown(uid_active, uid2, uid3) {
        uid_active.enabled = !uid_active.enabled;
        uid_active.opacity = !uid_active.opacity;
        uid2.enabled = false;
        uid2.opacity = 0;
        uid3.enabled = false;
        uid3.opacity = 0;
    }

    function activate_config(overlay, prefImg) {
        overlay.enabled = false;
        overlay.opacity = 0;
        prefImg.enabled = true;
    }

    function enable_calibration() {
        if (prefSceneImg.enabled && prefLeftEyeImg.enabled && prefRightEyeImg.enabled) {
            calibration.enabled = true;
            calibrationDisabledOverlay.opacity = 0;
        }
    }

    /*
      CALIBRATION CONTOL
      ------------------ */
    GroupBox {
        id: calibrationSettings
        x: 30
        y: 16
        width: 315
        height: 110
        label: Text {
            color:"gray"
            text:"Calibration Settings"
        }
        ColumnLayout {
            y:0
            Layout.fillHeight: false
            Layout.fillWidth: false
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

            Text {
                id: calibrationLabel
                text: qsTr("Calibrate")
                color: "white"
                horizontalAlignment: Text.AlignHCenter
            }
            Image {
                id: calibration
                sourceSize.width: 50
                sourceSize.height: 50
                fillMode: Image.PreserveAspectFit
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                source: "../imgs/calibration.png"
                //enabled: false <--DEBUG!
                z:1

                ColorOverlay {
                    id: calibrationDisabledOverlay
                    anchors.fill: calibration
                    source: calibration
                    color: "#555555"
                    opacity: 1
                }

                ColorOverlay {
                    id: calibrationOverlay
                    anchors.fill: calibration
                    source: calibration
                    color: "white"
                    opacity: 0
                }

                MouseArea {
                    id: calibrationBtn
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    anchors.fill: parent
                    onEntered: {
                        calibrationOverlay.opacity = 1
                    }
                    onExited: {
                        calibrationOverlay.opacity = 0
                    }
                    onClicked: {
                        //calibScreen.showFullScreen();
                        calibScreen.showNormal();
                    }
                }
            }
        }

        ColumnLayout {
            x: 75
            y:0
            Layout.fillHeight: false
            Layout.fillWidth: false
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

            Text {
                id: calibrationModeLabel
                text: qsTr("Mode")
                color: "white"
                horizontalAlignment: Text.AlignHCenter
            }
            ComboBox {
                id: calibrationModeBox
                width: 110
                height: 28
                currentIndex: 0
                z: 1
                font.pointSize: 10
                model: ["Screen", "HMD"]
                onActivated:  {
                    console.log("selected:", index);
                }
            }
        }
        ColumnLayout {
            x: 220
            y:0
            Layout.fillHeight: false
            Layout.fillWidth: false
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

            Text {
                id: calibrationStoreLabel
                text: qsTr("Store Data")
                color: "white"
                horizontalAlignment: Text.AlignHCenter
            }
            Switch {
                id: switchStore
                width: 60
                height: 40
                checked: false
                font.pointSize: 8
                onToggled: {
                    console.log(position);
                }
            }
        }
    }

    /*CALIB SCREEN
      ------------*/
    CalibScreen {
        id: calibScreen
        visible: false
        height: 720
        width: 1280
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
                enabled: false
                z:1

                ColorOverlay {
                    id: sceneDisabledOverlay
                    anchors.fill: prefSceneImg
                    source: prefSceneImg
                    color: "#555555"
                    opacity: 1
                }

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
                        update_comboboxes(scenePrefDropdown, sceneCam);
                        activate_dropdown(scenePrefDropdown, leftEyePrefDropdown, rightEyePrefDropdown);
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
                        update_comboboxes(scenePrefDropdown, sceneCam);
                    }
                    comboResolution.onActivated: {
                        sceneCam.set_mode(comboFrameRate.currentText, comboResolution.currentText);
                        update_comboboxes(scenePrefDropdown, sceneCam);
                    }
                    dialGamma.onMoved: {
                        sceneCam.set_gamma(dialGamma.value);
                    }
                    switchColor.onToggled: {
                        sceneCam.set_color(switchColor.position);
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
                enabled: false
                z:1

                ColorOverlay {
                    id: leftEyeDisabledOverlay
                    anchors.fill: prefLeftEyeImg
                    source: prefLeftEyeImg
                    color: "#555555"
                    opacity: 1
                }

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
                        update_comboboxes(leftEyePrefDropdown, leftEyeCam);
                        activate_dropdown(leftEyePrefDropdown, scenePrefDropdown, rightEyePrefDropdown);
                    }
                }
                Dropdown {
                    id:leftEyePrefDropdown
                    x: -143
                    y: 49
                    enabled: false;
                    opacity: 0;
                    comboFrameRate.onActivated: {
                        leftEyeCam.set_mode(comboFrameRate.currentText, comboResolution.currentText);
                        update_comboboxes(leftEyePrefDropdown, leftEyeCam);
                    }
                    comboResolution.onActivated: {
                        leftEyeCam.set_mode(comboFrameRate.currentText, comboResolution.currentText);
                        update_comboboxes(leftEyePrefDropdown, leftEyeCam);
                    }
                    dialGamma.onMoved: {
                        leftEyeCam.set_gamma(dialGamma.value);
                    }
                    switchColor.onToggled: {
                        leftEyeCam.set_color(switchColor.position);
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
                enabled: false
                z:1

                ColorOverlay {
                    id: rightEyeDisabledOverlay
                    anchors.fill: prefRightEyeImg
                    source: prefRightEyeImg
                    color: "#555555"
                    opacity: 1
                }

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
                        update_comboboxes(rightEyePrefDropdown, rightEyeCam);
                        activate_dropdown(rightEyePrefDropdown, scenePrefDropdown, leftEyePrefDropdown);
                    }
                }
                Dropdown {
                    id:rightEyePrefDropdown
                    x: -143
                    y: 49
                    enabled: false;
                    opacity: 0;
                    comboFrameRate.onActivated: {
                        rightEyeCam.set_mode(comboFrameRate.currentText, comboResolution.currentText);
                        update_comboboxes(rightEyePrefDropdown, rightEyeCam);
                    }
                    comboResolution.onActivated: {
                        rightEyeCam.set_mode(comboFrameRate.currentText, comboResolution.currentText);
                        update_comboboxes(rightEyePrefDropdown, rightEyeCam);
                    }
                    dialGamma.onMoved: {
                        rightEyeCam.set_gamma(dialGamma.value);
                    }
                    switchColor.onToggled: {
                        rightEyeCam.set_color(switchColor.position);
                    }
                }
            }
        }
    }
}
