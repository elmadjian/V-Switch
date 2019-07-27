import QtQuick 2.0
import QtQuick.Controls 2.5
import QtQuick.Controls.Universal 2.3
import QtMultimedia 5.12

Item {
    width: 640
    height: 480

    Camera {
        id: camera
        imageCapture {
            onImageCaptured: {
               framePreview.source = preview
            }
        }
    }

    VideoOutput {
        source: camera
        anchors.fill: parent
        focus: visible
    }

    Image {
        id: framePreview
    }
}
