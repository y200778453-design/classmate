import QtQuick
import ClassMateTheme

Item {
    id: root
    property bool active: false
    property real level: 0.0
    width: 180
    height: 48

    Row {
        id: barRow
        anchors.centerIn: parent
        spacing: 5
        Repeater {
            id: barRepeater
            model: 14
            Rectangle {
                property real target: 0.04
                width: 6
                radius: 3
                anchors.verticalCenter: parent.verticalCenter
                height: 4 + target * 42
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Theme.accent }
                    GradientStop { position: 1.0; color: Theme.cyan }
                }
                Behavior on height { NumberAnimation { duration: 110; easing.type: Theme.easeOut } }
            }
        }
    }

    Timer {
        interval: 110
        running: root.active
        repeat: true
        onTriggered: {
            for (var i = 0; i < barRepeater.count; i++) {
                var wavePhase = 0.25 + 0.75 * Math.abs(Math.sin(i * 1.9 + Date.now() / 260))
                barRepeater.itemAt(i).target = root.active ? (0.1 + 0.9 * root.level) * wavePhase : 0.04
            }
        }
    }
}
