import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ClassMateTheme
import ClassMate.Core
import "../components"

Item {
    id: page

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.s5
        spacing: Theme.s4

        RowLayout {
            ColumnLayout {
                spacing: 2
                CmText { text: "課堂智聽"; font.pixelSize: 26; font.bold: true }
                CmText { text: Bridge.statusText; font.pixelSize: 12; color: Theme.textSecondary }
            }
            Item { Layout.fillWidth: true }
            Rectangle {
                Layout.preferredWidth: 84
                Layout.preferredHeight: 34
                radius: 17
                color: Bridge.listening ? "#2E3DDC97" : "#1AFFFFFF"
                border.color: Bridge.listening ? "#663DDC97" : Theme.border
                RowLayout {
                    anchors.centerIn: parent
                    spacing: 6
                    Rectangle {
                        width: 8
                        height: 8
                        radius: 4
                        color: Bridge.listening ? Theme.success : Theme.textDim
                        SequentialAnimation on opacity {
                            running: Bridge.listening
                            loops: Animation.Infinite
                            NumberAnimation { from: 1; to: 0.25; duration: 700; easing.type: Theme.easeLinear }
                            NumberAnimation { from: 0.25; to: 1; duration: 700; easing.type: Theme.easeLinear }
                        }
                    }
                    CmText { text: Bridge.listening ? "聆聽中" : "待機"; font.pixelSize: 12; color: Bridge.listening ? Theme.success : Theme.textDim }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            PulseRing {
                anchors.centerIn: parent
                active: Bridge.listening
                level: Bridge.audioLevel
                size: Math.min(parent.width * 0.64, 252)
            }

            WaveBars {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 6
                active: Bridge.listening
                level: Bridge.audioLevel
            }
        }

        GlassCard {
            Layout.fillWidth: true
            Layout.preferredHeight: 54

            CmText {
                anchors.centerIn: parent
                width: parent.width - 32
                text: Bridge.transcript ? Bridge.transcript : "⋯ 等待老師發言（粵 · 英 · 普）"
                color: Bridge.transcript ? Theme.cyan : Theme.textDim
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
            }
        }

        RowLayout {
            spacing: Theme.s3
            Rectangle {
                Layout.preferredWidth: subjectLabel.implicitWidth + 32
                Layout.preferredHeight: 36
                radius: 18
                color: "#1F6C8CFF"
                border.color: "#4D6C8CFF"
                scale: subjectMouse.pressed ? 0.95 : 1.0
                Behavior on scale { NumberAnimation { duration: Theme.dFast; easing.type: Theme.easeBack } }
                RowLayout {
                    anchors.centerIn: parent
                    spacing: 6
                    CmText { text: "✦"; font.pixelSize: 12; color: Theme.cyan }
                    CmText {
                        id: subjectLabel
                        text: Bridge.currentSubjectName || "選擇科目"
                        font.pixelSize: 12
                        color: "#DCE4FF"
                    }
                }
                MouseArea {
                    id: subjectMouse
                    anchors.fill: parent
                    onClicked: Window.window.switchPage(1)
                }
            }
            Item { Layout.fillWidth: true }
            CmText {
                text: "今日 " + Bridge.stats.today + " · 共 " + Bridge.stats.total
                font.pixelSize: 12
                color: Theme.textDim
            }
        }

        GlassCard {
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.s3

                RowLayout {
                    CmText { text: "作答模式"; font.pixelSize: 13; color: Theme.textSecondary }
                    Item { Layout.fillWidth: true }
                    ModePill {
                        mode: Bridge.answerMode
                        onModePicked: function(m) { Bridge.setAnswerMode(m) }
                    }
                }

                CmText { text: "識別靈敏度 " + Bridge.sensitivity; font.pixelSize: 12; color: Theme.textDim }

                SensitivitySlider {
                    Layout.fillWidth: true
                    value: Bridge.sensitivity
                    onValuePicked: function(v) { Bridge.setSensitivity(v) }
                }
            }
        }

        PrimaryButton {
            objectName: "mainStartButton"
            Layout.fillWidth: true
            text: Bridge.listening ? "暫停聆聽" : "開始聆聽"
            color1: Bridge.listening ? Theme.danger : Theme.accent
            color2: Bridge.listening ? "#FF2E63" : Theme.accent2
            onClicked: Bridge.toggleListening()
        }
    }
}
