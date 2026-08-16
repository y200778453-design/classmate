import QtQuick
import ClassMateTheme

Item {
    id: root
    property int current: 0
    signal selected(int index)
    height: 84

    readonly property var icons: ["◉", "✦", "◷", "⚙"]
    readonly property var labels: ["監聽", "科目", "歷史", "設定"]

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0017192E" }
            GradientStop { position: 1.0; color: "#E617192E" }
        }
    }

    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 8
        Repeater {
            model: 4
            Item {
                width: (parent.parent.width) / 4
                height: 68
                property bool sel: root.current === index

                Rectangle {
                    width: 46
                    height: 34
                    radius: 17
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    color: sel ? "#2E6C8CFF" : "transparent"
                    scale: sel ? 1.0 : 0.62
                    Behavior on scale { NumberAnimation { duration: Theme.dSwitch; easing.type: Theme.easeBack } }
                    Behavior on color { ColorAnimation { duration: Theme.dBase; easing.type: Theme.easeOut } }
                }
                Column {
                    anchors.centerIn: parent
                    spacing: 2
                    CmText {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: root.icons[index]
                        font.pixelSize: 19
                        color: sel ? "#FFFFFF" : Theme.textSecondary
                        Behavior on color { ColorAnimation { duration: Theme.dBase } }
                    }
                    CmText {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: root.labels[index]
                        font.pixelSize: 11
                        color: sel ? "#FFFFFF" : Theme.textDim
                        Behavior on color { ColorAnimation { duration: Theme.dBase } }
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.selected(index)
                }
            }
        }
    }
}
