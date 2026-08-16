import QtQuick
import ClassMateTheme

Rectangle {
    id: root
    color: Theme.card
    radius: Theme.rLg
    border.color: Theme.border
    border.width: 1

    Item {
        id: body
        anchors.fill: parent
        anchors.margins: Theme.s4
    }

    default property alias content: body.data
}
