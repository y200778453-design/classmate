import QtQuick
import QtQuick.Controls.Basic
import ClassMateTheme

Item {
    id: root
    property int value: 55
    signal valuePicked(int v)
    height: 62

    Slider {
        id: slider
        from: 0
        to: 100
        stepSize: 1
        value: root.value
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16

        background: Rectangle {
            height: 8
            radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: "#2AFFFFFF"
            Rectangle {
                width: parent.width * slider.position
                height: 8
                radius: 4
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Theme.accent }
                    GradientStop { position: 1.0; color: Theme.cyan }
                }
            }
        }

        handle: Rectangle {
            x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
            y: slider.topPadding + slider.availableHeight / 2 - height / 2
            implicitWidth: 26
            implicitHeight: 26
            radius: 13
            color: "#FFFFFF"
            border.width: 5
            border.color: Theme.accent
        }

        onMoved: root.valuePicked(Math.round(value))
    }

    Row {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        CmText { width: parent.width / 3; text: "溫柔"; font.pixelSize: 10; color: Theme.textDim; horizontalAlignment: Text.AlignLeft }
        CmText { width: parent.width / 3; text: "標準"; font.pixelSize: 10; color: Theme.textSecondary; horizontalAlignment: Text.AlignHCenter }
        CmText { width: parent.width / 3; text: "敏銳"; font.pixelSize: 10; color: Theme.textSecondary; horizontalAlignment: Text.AlignRight }
    }
}
