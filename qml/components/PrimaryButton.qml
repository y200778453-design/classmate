import QtQuick
import ClassMateTheme

Rectangle {
    id: root
    property string text: ""
    property color color1: Theme.accent
    property color color2: Theme.accent2
    signal clicked()
    height: 52
    radius: 26
    gradient: Gradient {
        GradientStop { position: 0.0; color: root.color1 }
        GradientStop { position: 1.0; color: root.color2 }
    }
    scale: area.pressed ? 0.94 : 1.0
    Behavior on scale { NumberAnimation { duration: Theme.dFast; easing.type: Theme.easeBack } }

    CmText {
        anchors.centerIn: parent
        text: root.text
        color: "#FFFFFF"
        font.pixelSize: 16
        font.bold: true
    }

    MouseArea {
        id: area
        anchors.fill: parent
        onClicked: root.clicked()
    }
}
