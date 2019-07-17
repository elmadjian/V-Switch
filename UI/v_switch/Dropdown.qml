import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Controls.Universal 2.2
import QtGraphicalEffects 1.0



Rectangle {
    id: dropdown
    width:175
    height:260
    color: "#424242"
    Universal.theme: Universal.Dark
    Universal.accent: Universal.Lime
    z: 2

    Text {
        id: textFrameRate
        x: 25
        y: 24
        color: "#ffffff"
        text: qsTr("Frame Rate")
        font.pixelSize: 12
    }

    ComboBox {
        id: comboFrameRate
        x: 25
        y: 44
        width: 125
        height: 25
    }

    Text {
        id: textResolution
        x: 25
        y: 89
        color: "#ffffff"
        text: qsTr("Resolution")
        font.pixelSize: 12
    }

    ComboBox {
        id: comboResolution
        x: 25
        y: 108
        width: 125
        height: 25
    }

    Text {
        id: textContrast
        x: 25
        y: 157
        color: "#ffffff"
        text: qsTr("Contrast")
        font.pixelSize: 12
    }

    Dial {
        id: dialContrast
        x: 23
        y: 167
        width: 56
        height: 88
        wheelEnabled: false
        background: Rectangle {
            x: dialContrast.width / 2 - width / 2
            y: dialContrast.height / 2 - height / 2
            width: Math.max(64, Math.min(dialContrast.width, dialContrast.height))
            height: width
            color: "transparent"
            radius: width / 2
            border.color: dialContrast.pressed ? "white" : "gray"
            opacity: dialContrast.enabled ? 1 : 0.3
        }
        handle: Rectangle {
            id: handleItem
            x: dialContrast.background.x + dialContrast.background.width / 2 - width / 2
            y: dialContrast.background.y + dialContrast.background.height / 2 - height / 2
            width: 15
            height: 15
            color: dialContrast.pressed ? "#white" : "gray"
            radius: 8
            border.width: 0
            antialiasing: true
            opacity: dialContrast.enabled ? 1 : 0.3
            transform: [
                Translate {
                    y: -Math.min(dialContrast.background.width, dialContrast.background.height) * 0.4 + handleItem.height / 2
                },
                Rotation {
                    angle: dialContrast.angle
                    origin.x: handleItem.width / 2
                    origin.y: handleItem.height / 2
                }
            ]
        }
    }


    Text {
        id: textColor
        x: 115
        y: 157
        color: "#ffffff"
        text: qsTr("Color")
        font.pixelSize: 12
    }

    Switch {
        id: switchColor
        x: 99
        y: 185
        width: 61
        height: 44
        padding: 0
        rightPadding: 4
        bottomPadding: 4
        leftPadding: 4
        topPadding: 4
        spacing: 5
        checked: true
        font.pointSize: 8
    }

    Image {
        id: triangle
        x: 147
        y: 3
        width: 25
        height: 25
        source: "../imgs/triangle.png"

        ColorOverlay {
            id: triangleOverlay
            anchors.fill: triangle
            source: triangle
            color: "white"
            opacity: 0
        }


        MouseArea {
            hoverEnabled: true
            id:closeDropdown
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor;
            onEntered: {
                triangleOverlay.opacity = 1;
            }
            onExited: {
                triangleOverlay.opacity = 0;
            }
            onClicked: {
                dropdown.opacity = 0;
                dropdown.enabled = false;
            }
        }
    }
}


