import QtQuick
import ClassMateTheme

Item {
    id: root
    property string mode: "concise"
    signal modePicked(string m)
    width: 190
    height: 40

    Rectangle {
        anchors.fill: parent
        radius: 20
        color: "#1AFFFFFF"
        border.color: Theme.border
    }

    Rectangle {
        id: indicator
        width: (parent.width - 8) / 2
        height: parent.height - 8
        radius: 16
        y: 4
        x: 4 + (root.mode === "deep" ? (parent.width - 8) / 2 : 0)
        Behavior on x { NumberAnimation { duration: Theme.dSwitch; easing.type: Theme.easeBack } }
        gradient: Gradient {
            GradientStop { position: 0.0; color: Theme.accent }
            GradientStop { position: 1.0; color: Theme.accent2 }
        }
    }

    Repeater {
        model: ["簡潔", "深入研討"]
        Item {
            width: parent.width / 2
            height: parent.height
            x: index * width
            CmText {
                anchors.centerIn: parent
                text: modelData
                font.pixelSize: 13
                font.bold: (root.mode === "concise") === (index === 0)
                color: (root.mode === "concise") === (index === 0) ? "#FFFFFF" : Theme.textSecondary
                Behavior on color { ColorAnimation { duration: Theme.dBase } }
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    var m = index === 0 ? "concise" : "deep"
                    if (m !== root.mode) {
                        root.mode = m
                        root.modePicked(m)
                    }
                }
            }
        }
    }
}
