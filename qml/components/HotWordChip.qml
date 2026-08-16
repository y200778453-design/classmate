import QtQuick
import ClassMateTheme

Rectangle {
    id: root
    property string term: ""
    property bool custom: false
    signal clicked()
    signal removeRequested()
    height: 34
    width: label.implicitWidth + (custom ? 46 : 28)
    radius: 17
    color: custom ? "#2EFFB020" : "#1F6C8CFF"
    border.color: custom ? "#66FFB020" : "#4D6C8CFF"
    border.width: 1
    scale: area.pressed ? 0.92 : 1.0
    Behavior on scale { NumberAnimation { duration: Theme.dFast; easing.type: Theme.easeBack } }

    Row {
        anchors.centerIn: parent
        spacing: 6
        CmText {
            id: label
            text: root.term
            font.pixelSize: 12
            color: custom ? Theme.warning : "#DCE4FF"
        }
        CmText {
            visible: root.custom
            text: "×"
            font.pixelSize: 14
            font.bold: true
            color: Theme.warning
            MouseArea {
                anchors.fill: parent
                width: 16
                height: 16
                onClicked: root.removeRequested()
            }
        }
    }

    MouseArea {
        id: area
        anchors.fill: parent
        onClicked: root.clicked()
    }
}
