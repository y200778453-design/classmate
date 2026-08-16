import QtQuick
import ClassMateTheme

Rectangle {
    id: root
    property var subject: null
    property bool selected: false
    signal clicked()
    width: 136
    height: 96
    radius: Theme.rMd
    color: selected ? "#26FFFFFF" : Theme.card
    border.width: selected ? 1.5 : 1
    border.color: selected ? (subject ? subject.color : Theme.accent) : Theme.border
    scale: mouseArea.pressed ? 0.94 : 1.0
    Behavior on scale { NumberAnimation { duration: Theme.dFast; easing.type: Theme.easeBack } }
    Behavior on border.color { ColorAnimation { duration: Theme.dBase } }

    Column {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.margins: Theme.s3
        spacing: 4
        CmText {
            anchors.horizontalCenter: parent.horizontalCenter
            text: subject ? subject.icon : "✦"
            font.pixelSize: 24
        }
        CmText {
            width: parent.width
            text: subject ? subject.name : ""
            font.pixelSize: 12
            font.bold: selected
            color: selected ? Theme.textPrimary : Theme.textSecondary
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
            maximumLineCount: 2
            wrapMode: Text.Wrap
        }
        CmText {
            anchors.horizontalCenter: parent.horizontalCenter
            text: subject ? (subject.kind + " · " + subject.hotwords.length + " 詞") : ""
            font.pixelSize: 10
            color: Theme.textDim
        }
    }

    Rectangle {
        visible: root.selected
        width: 20
        height: 20
        radius: 10
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 8
        color: subject ? subject.color : Theme.accent
        CmText {
            anchors.centerIn: parent
            text: "✓"
            color: "#FFFFFF"
            font.pixelSize: 12
            font.bold: true
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        onClicked: root.clicked()
    }
}
