import QtQuick
import ClassMateTheme

Item {
    id: root
    property bool active: false
    property real level: 0.0
    property color ringColor: Theme.accent
    property int size: 240

    width: size
    height: size

    Repeater {
        model: 3
        Rectangle {
            property int idx: index
            anchors.centerIn: parent
            width: root.size * 0.44
            height: width
            radius: width / 2
            color: "transparent"
            border.color: root.ringColor
            border.width: 2
            opacity: root.active ? 0.5 - idx * 0.15 : 0.1
            scale: 0.95
            Behavior on opacity { NumberAnimation { duration: Theme.dBase; easing.type: Theme.easeOut } }
            SequentialAnimation on scale {
                id: ringLoop
                running: root.active
                loops: Animation.Infinite
                PauseAnimation { duration: idx * 320 }
                NumberAnimation { from: 0.95; to: 2.05; duration: 2400; easing.type: Theme.easeLinear }
                NumberAnimation { from: 2.05; to: 0.95; duration: 0 }
                PauseAnimation { duration: (3 - idx) * 380 }
            }
        }
    }

    Rectangle {
        anchors.centerIn: parent
        width: root.size * 0.42
        height: width
        radius: width / 2
        gradient: Gradient {
            GradientStop { position: 0.0; color: Theme.accent }
            GradientStop { position: 1.0; color: Theme.accent2 }
        }
        scale: root.active ? 1.0 + root.level * 0.08 : 1.0
        Behavior on scale { NumberAnimation { duration: 130; easing.type: Theme.easeOut } }

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * 0.86
            height: width
            radius: width / 2
            color: "transparent"
            border.color: "#55FFFFFF"
            border.width: 1.5
        }

        CmText {
            anchors.centerIn: parent
            text: "◉"
            color: "#FFFFFF"
            font.pixelSize: 44
            opacity: root.active ? 0.95 : 0.75
        }
    }
}
