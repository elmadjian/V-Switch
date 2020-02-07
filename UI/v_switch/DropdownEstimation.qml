import QtQuick 2.9
//import QtQuick.Window 2.3
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.0
import QtQuick.Controls.Universal 2.2
import QtGraphicalEffects 1.0

Rectangle {
    id: dropdownEstimation
    height: 472
    width: 839
    color: "white"
    Universal.theme: Universal.Dark
    Universal.accent: Universal.Lime
    z: 2

    signal drawEstimation(var a, var b, var c)
    property var targetList
    property var leftEyeList;
    property var rightEyeList;

    Component.onCompleted: {
        calibControl.draw_estimation.connect(drawEstimation);
    }

    onDrawEstimation: {
        console.log('signal received');
        targetList = a;
        leftEyeList = b;
        rightEyeList = c;
        canvasArea.requestPaint();
    }

    function drawCrossHair(coord, ctx, color, width) {
        var x = coord[0];
        var y = coord[1];
        ctx.strokeWidth = width;
        ctx.strokeStyle = color;
        ctx.moveTo(x,y-10);
        ctx.lineTo(x,y+10);
        ctx.moveTo(x-10,y);
        ctx.lineTo(x+10,y);
        ctx.stroke();
    }

    function denormalize(coord) {
        var newX = coord[0] * dropdownEstimation.width;
        var newY = coord[1] * dropdownEstimation.height;
        var x = Math.floor(newX)+0.5;
        var y = Math.floor(newY)+0.5;
        return [x, y];
    }


    Canvas {
        id: canvasArea
        anchors.fill: parent
        onPaint: {
            console.log("painting now");
            var ctx = getContext("2d");
           // drawCrossHair([0.1, 0.1], ctx, "red", 2);
            for (var i = 0; i < targetList.length; i++) {
                //console.log(targetList[i]);
                var vec = denormalize(targetList[i]);
                var x = vec[0];
                var y = vec[1];
                ctx.strokeWidth = 3;
                ctx.strokeStyle = "black";
                ctx.moveTo(x,y-10);
                ctx.lineTo(x,y+10);
                ctx.moveTo(x-10,y);
                ctx.lineTo(x+10,y);
                ctx.stroke();
                vec = denormalize(leftEyeList[i]);
                x = vec[0];
                y = vec[1];
                ctx.strokeWidth = 3;
                ctx.strokeStyle = "red";
                ctx.moveTo(x,y-10);
                ctx.lineTo(x,y+10);
                ctx.moveTo(x-10,y);
                ctx.lineTo(x+10,y);
                ctx.stroke();

            }

        }
    }

    Image {
        id: triangle
        x: 3
        y: 3
        width: 25
        height: 25
        antialiasing: true
        rotation: 270
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
                dropdownEstimation.enabled = false;
                dropdownEstimation.opacity = 0;
            }
        }
    }
}
