import QtQuick
import ClassMateTheme

Item {
    id: root
    anchors.fill: parent

    function show(text, kind) {
        msg.text = text
        box.color = kind === "error" ? "#F02B1E3F" : (kind === "ok" ? "#F01F3D33" : "#F01B2745")
        box.visible = true
        box.opacity = 1
        hideTimer.restart()
    }

    Timer {
        id: hideTimer
        interval: 2600
        onTriggered: hideAnim.start()
    }

    NumberAnimation {
        id: hideAnim
        target: box
        property: "opacity"
        to: 0
        duration: 300
        easing.type: Theme.easeOut
    }

    Rectangle {
        id: box
        visible: false
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.76
        width: Math.min(parent.width - 64, 340)
        height: 46
        radius: 23
        color: Theme.popupBg
        border.color: Theme.border
        CmText {
            id: msg
            anchors.centerIn: parent
            font.pixelSize: 13
            color: Theme.textPrimary
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
