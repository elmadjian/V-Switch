import QtQuick 2.9
import QtQuick.Window 2.3
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.0

Window {
    id: calibTest
    height: 720
    width: 1280
    color: "white"

    signal drawCalibration()

    Component.onCompleted: {
        calibControl.draw_calibration.connect(drawCalibration);
    }

    onDrawCalibration: {
        console.log('signal received');
    }

    Canvas {
        id: canvasArea
        anchors.fill: parent

    }


}
