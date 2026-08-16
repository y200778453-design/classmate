import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ClassMateTheme
import ClassMate.Core

Item {
    id: root
    objectName: "alertPopup"
    anchors.fill: parent
    visible: false
    z: 50

    property var ev: null
    property string mode: "concise"
    property string shownAnswer: ""
    property int reveal: 0
    property int chunk: 1

    function show(event) {
        ev = event
        mode = event.mode || "concise"
        shownAnswer = event.answer || ""
        reveal = 0
        chunk = Math.max(1, Math.round(shownAnswer.length / 150))
        root.visible = true
        card.visible = true
        scrim.opacity = 1
        dropAnim.from = -card.height - 24
        dropAnim.to = 14
        dropAnim.restart()
        fadeIn.restart()
        typeTimer.restart()
        autoClose.interval = event.urgent ? 20000 : 14000
        autoClose.restart()
    }

    function closeNow() {
        dropAnim.to = -card.height - 24
        dropAnim.restart()
        scrim.opacity = 0
        exitTimer.start()
    }

    function refreshAnswer() {
        if (!ev)
            return
        var r = Bridge.reAnswer(ev.id, ev.question, mode)
        shownAnswer = r.answer
        reveal = 0
        chunk = Math.max(1, Math.round(shownAnswer.length / 150))
        typeTimer.restart()
    }

    Timer { id: exitTimer; interval: 260; onTriggered: { root.visible = false; card.visible = false } }
    Timer { id: typeTimer; interval: 12; repeat: true; onTriggered: {
        if (reveal < shownAnswer.length)
            reveal += chunk
        else
            stop()
    } }
    Timer { id: autoClose; interval: 14000; onTriggered: root.closeNow() }

    Rectangle {
        id: scrim
        anchors.fill: parent
        color: Theme.scrim
        opacity: 0
        Behavior on opacity { NumberAnimation { duration: Theme.dBase; easing.type: Theme.easeOut } }
        MouseArea { anchors.fill: parent; onClicked: root.closeNow() }
    }

    Rectangle {
        id: card
        objectName: "alertCard"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        width: parent.width - 32
        height: Math.min(parent.height * 0.6, 460)
        y: 14
        visible: false
        radius: Theme.rLg
        color: ev && ev.urgent ? Theme.popupUrgentBg : Theme.popupBg
        border.width: 1.5
        border.color: ev && ev.urgent ? Theme.danger : "#3DFFFFFF"
        opacity: 0

        NumberAnimation on y { id: dropAnim; duration: Theme.dPopup; easing.type: Theme.easeBack }
        NumberAnimation on opacity { id: fadeIn; from: 0; to: 1; duration: Theme.dBase; easing.type: Theme.easeOut }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.s4
            spacing: Theme.s3

            RowLayout {
                Rectangle {
                    Layout.preferredWidth: badgeText.implicitWidth + 20
                    Layout.preferredHeight: 26
                    radius: 13
                    color: ev && ev.urgent ? "#59FF5C7A" : "#5935E0FF"
                    CmText {
                        id: badgeText
                        objectName: "alertBadge"
                        anchors.centerIn: parent
                        text: ev && ev.urgent ? "⚠ 點名！請回答" : "✦ 課堂提問"
                        font.pixelSize: 12
                        font.bold: true
                        color: "#FFFFFF"
                    }
                }
                CmText {
                    Layout.fillWidth: true
                    text: ev ? ev.subjectName : ""
                    font.pixelSize: 12
                    color: Theme.textSecondary
                    elide: Text.ElideRight
                }
                Rectangle {
                    Layout.preferredWidth: 30
                    Layout.preferredHeight: 30
                    radius: 15
                    color: "#22FFFFFF"
                    CmText { anchors.centerIn: parent; text: "×"; font.pixelSize: 16; color: Theme.textSecondary }
                    MouseArea { anchors.fill: parent; onClicked: root.closeNow() }
                }
            }

            CmText {
                Layout.fillWidth: true
                text: ev ? ev.question : ""
                font.pixelSize: 16
                font.bold: true
                wrapMode: Text.Wrap
                maximumLineCount: 3
                elide: Text.ElideRight
            }

            Row {
                visible: ev && ev.hotwords && ev.hotwords.length > 0
                spacing: 6
                Repeater {
                    model: ev ? ev.hotwords : []
                    Rectangle {
                        height: 22
                        width: tagText.implicitWidth + 16
                        radius: 11
                        color: "#2E9B6CFF"
                        border.color: "#4D9B6CFF"
                        CmText {
                            id: tagText
                            anchors.centerIn: parent
                            text: modelData
                            font.pixelSize: 11
                            color: "#DCE4FF"
                        }
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: Theme.border }

            Flickable {
                id: flick
                Layout.fillWidth: true
                Layout.preferredHeight: 172
                contentHeight: answerText.implicitHeight
                clip: true
                CmText {
                    id: answerText
                    objectName: "alertAnswerText"
                    width: flick.width - 8
                    text: shownAnswer.substring(0, reveal)
                    wrapMode: Text.Wrap
                    font.pixelSize: 14
                    lineHeight: 1.35
                }
            }

            RowLayout {
                ModePill {
                    mode: root.mode
                    onModePicked: function(m) { root.mode = m; root.refreshAnswer() }
                }
                Item { Layout.fillWidth: true }
                Rectangle {
                    Layout.preferredWidth: copyText.implicitWidth + 32
                    Layout.preferredHeight: 36
                    radius: 18
                    color: "#26FFFFFF"
                    border.color: Theme.border
                    CmText {
                        id: copyText
                        anchors.centerIn: parent
                        text: "複製"
                        font.pixelSize: 13
                        color: Theme.textPrimary
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: Bridge.copyText(shownAnswer)
                    }
                }
            }
        }
    }

    Connections {
        target: Bridge
        function onAnswerReady(r) {
            if (!ev || r.id !== ev.id)
                return
            if (r.source === "api" && r.answer) {
                shownAnswer = r.answer
                reveal = 0
                chunk = Math.max(1, Math.round(shownAnswer.length / 150))
                typeTimer.restart()
            } else if (r.source === "api-error") {
                shownAnswer = "⚠ AI 接駁失敗：" + (r.error || "") + "\n\n（以下為離線答題框架，可先在「設定」檢查 AI 接駁。）"
                reveal = 0
                typeTimer.restart()
            }
        }
    }
}
