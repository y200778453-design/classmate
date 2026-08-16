import QtQuick
import ClassMateTheme

Item {
    id: root
    property bool on: false
    signal toggled(bool value)
    width: 54
    height: 32

    Rectangle {
        anchors.fill: parent
        radius: 16
        color: root.on ? Theme.success : "#2AFFFFFF"
        Behavior on color { ColorAnimation { duration: Theme.dBase; easing.type: Theme.easeOut } }
        Rectangle {
            width: 26
            height: 26
            radius: 13
            anchors.verticalCenter: parent.verticalCenter
            x: root.on ? parent.width - width - 3 : 3
            color: "#FFFFFF"
            Behavior on x { NumberAnimation { duration: Theme.dSwitch; easing.type: Theme.easeBack } }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            root.on = !root.on
            root.toggled(root.on)
        }
    }
}
