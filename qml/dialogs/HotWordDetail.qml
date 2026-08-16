import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ClassMateTheme
import "../components"

Item {
    id: root
    anchors.fill: parent
    visible: false
    z: 55

    function show(hw) {
        term.text = hw.term
        aliases.text = hw.aliases && hw.aliases.length > 0 ? "亦稱：" + hw.aliases.join(" / ") : ""
        concise.text = hw.concise
        deep.text = hw.deep
        root.visible = true
        card.opacity = 0
        card.scale = 0.9
        fadeIn.restart()
        popIn.restart()
    }
    function close() {
        fadeOut.restart()
        exitTimer.start()
    }

    Timer { id: exitTimer; interval: 150; onTriggered: root.visible = false }
    NumberAnimation { id: fadeIn; target: card; property: "opacity"; from: 0; to: 1; duration: Theme.dBase; easing.type: Theme.easeOut }
    NumberAnimation { id: fadeOut; target: card; property: "opacity"; from: 1; to: 0; duration: 150; easing.type: Theme.easeOut }
    NumberAnimation { id: popIn; target: card; property: "scale"; from: 0.9; to: 1.0; duration: Theme.dPopup; easing.type: Theme.easeBack }

    Rectangle {
        anchors.fill: parent
        color: Theme.scrim
        MouseArea { anchors.fill: parent; onClicked: root.close() }
    }

    Rectangle {
        id: card
        anchors.centerIn: parent
        width: parent.width - 40
        height: Math.min(col.implicitHeight + Theme.s8, parent.height - 80)
        radius: Theme.rLg
        color: Theme.popupBg
        border.color: Theme.border
        border.width: 1

        ColumnLayout {
            id: col
            anchors.fill: parent
            anchors.margins: Theme.s5
            spacing: Theme.s3

            RowLayout {
                CmText { id: term; Layout.fillWidth: true; font.pixelSize: 20; font.bold: true; elide: Text.ElideRight }
                Rectangle {
                    Layout.preferredWidth: 30
                    Layout.preferredHeight: 30
                    radius: 15
                    color: "#22FFFFFF"
                    CmText { anchors.centerIn: parent; text: "×"; font.pixelSize: 16; color: Theme.textSecondary }
                    MouseArea { anchors.fill: parent; onClicked: root.close() }
                }
            }
            CmText { id: aliases; font.pixelSize: 12; color: Theme.textSecondary; wrapMode: Text.Wrap }
            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: Theme.border }
            CmText { Layout.fillWidth: true; text: "簡潔重點"; font.pixelSize: 12; color: Theme.cyan; font.bold: true }
            CmText { id: concise; Layout.fillWidth: true; font.pixelSize: 13; color: Theme.textPrimary; wrapMode: Text.Wrap; lineHeight: 1.4 }
            CmText { Layout.fillWidth: true; text: "深入研討"; font.pixelSize: 12; color: Theme.accent; font.bold: true }
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: Math.min(deep.implicitHeight + 4, 160)
                clip: true
                CmText { id: deep; width: col.width - Theme.s2; font.pixelSize: 13; color: Theme.textSecondary; wrapMode: Text.Wrap; lineHeight: 1.5 }
            }
        }
    }
}
