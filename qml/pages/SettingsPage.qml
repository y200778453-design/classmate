import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ClassMateTheme
import ClassMate.Core
import "../components"

Item {
    id: page

    Flickable {
        id: flickable
        anchors.fill: parent
        contentHeight: contentColumn.implicitHeight + Theme.s6
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        ColumnLayout {
            id: contentColumn
            width: parent.width - Theme.s8
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: Theme.s5
            spacing: Theme.s4

            CmText { text: "設定"; font.pixelSize: 24; font.bold: true }

            GlassCard {
                Layout.fillWidth: true
                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.s3
                    CmText { text: "你的名字（點名即時提醒）"; font.pixelSize: 14; font.bold: true }
                    CmText {
                        Layout.fillWidth: true
                        text: "老師叫你名字時立即彈出警示，附上最近問題的簡潔答案。"
                        font.pixelSize: 11
                        color: Theme.textDim
                        wrapMode: Text.Wrap
                    }
                    RowLayout {
                        spacing: Theme.s2
                        CmTextField { id: nameZh; Layout.fillWidth: true; hint: "中文名"; text: Bridge.userName.zh }
                        CmTextField { id: nameEn; Layout.fillWidth: true; hint: "英文名"; text: Bridge.userName.en }
                        CmTextField { id: nameYue; Layout.fillWidth: true; hint: "粵語叫法"; text: Bridge.userName.yue }
                    }
                    PrimaryButton {
                        Layout.preferredWidth: 120
                        height: 40
                        radius: 20
                        text: "儲存"
                        onClicked: Bridge.setUserName(nameZh.text, nameEn.text, nameYue.text)
                    }
                }
            }

            GlassCard {
                Layout.fillWidth: true
                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.s3
                    CmText { text: "課堂語言"; font.pixelSize: 14; font.bold: true }
                    RowLayout {
                        spacing: Theme.s3
                        Rectangle {
                            Layout.preferredWidth: lang1.implicitWidth + 24
                            Layout.preferredHeight: 32
                            radius: 16
                            color: Bridge.languageState.yue ? "#2E3DDC97" : "#14FFFFFF"
                            border.color: Bridge.languageState.yue ? "#663DDC97" : Theme.border
                            CmText {
                                id: lang1
                                anchors.centerIn: parent
                                text: "粵語"
                                font.pixelSize: 12
                                color: Bridge.languageState.yue ? Theme.success : Theme.textSecondary
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: Bridge.setLanguages(!Bridge.languageState.yue, Bridge.languageState.zh, Bridge.languageState.en)
                            }
                        }
                        Rectangle {
                            Layout.preferredWidth: lang2.implicitWidth + 24
                            Layout.preferredHeight: 32
                            radius: 16
                            color: Bridge.languageState.zh ? "#2E6C8CFF" : "#14FFFFFF"
                            border.color: Bridge.languageState.zh ? "#666C8CFF" : Theme.border
                            CmText {
                                id: lang2
                                anchors.centerIn: parent
                                text: "普通話"
                                font.pixelSize: 12
                                color: Bridge.languageState.zh ? "#DCE4FF" : Theme.textSecondary
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: Bridge.setLanguages(Bridge.languageState.yue, !Bridge.languageState.zh, Bridge.languageState.en)
                            }
                        }
                        Rectangle {
                            Layout.preferredWidth: lang3.implicitWidth + 24
                            Layout.preferredHeight: 32
                            radius: 16
                            color: Bridge.languageState.en ? "#2EFFB020" : "#14FFFFFF"
                            border.color: Bridge.languageState.en ? "#66FFB020" : Theme.border
                            CmText {
                                id: lang3
                                anchors.centerIn: parent
                                text: "English"
                                font.pixelSize: 12
                                color: Bridge.languageState.en ? Theme.warning : Theme.textSecondary
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: Bridge.setLanguages(Bridge.languageState.yue, Bridge.languageState.zh, !Bridge.languageState.en)
                            }
                        }
                    }
                    CmText {
                        Layout.fillWidth: true
                        text: "引擎狀態：vosk " + (Bridge.engines.vosk ? "✓" : "—") + " · google " + (Bridge.engines.google ? "✓" : "—") + " · mock " + (Bridge.engines.mock ? "✓" : "—")
                        font.pixelSize: 11
                        color: Theme.textDim
                    }
                }
            }

            GlassCard {
                Layout.fillWidth: true
                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.s3
                    CmText { text: "作答模式"; font.pixelSize: 14; font.bold: true }
                    ModePill {
                        Layout.alignment: Qt.AlignHCenter
                        mode: Bridge.answerMode
                        onModePicked: function(m) { Bridge.setAnswerMode(m) }
                    }
                    CmText { text: "識別靈敏度 " + Bridge.sensitivity; font.pixelSize: 12; color: Theme.textDim }
                    SensitivitySlider {
                        Layout.fillWidth: true
                        value: Bridge.sensitivity
                        onValuePicked: function(v) { Bridge.setSensitivity(v) }
                    }
                }
            }

            GlassCard {
                Layout.fillWidth: true
                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.s3
                    RowLayout {
                        CmText { Layout.fillWidth: true; text: "AI 接駁（可選）"; font.pixelSize: 14; font.bold: true }
                        ToggleSwitch {
                            on: Bridge.apiState.enabled
                            onToggled: function(v) { Bridge.saveApi(v, apiBase.text, apiKey.text, apiModel.text) }
                        }
                    }
                    CmText {
                        Layout.fillWidth: true
                        text: "關閉＝離線模式（內建熱詞知識庫＋答題框架）。開啟＝接駁任何 OpenAI 相容 API 取得完整答案。"
                        font.pixelSize: 11
                        color: Theme.textDim
                        wrapMode: Text.Wrap
                        lineHeight: 1.4
                    }
                    CmTextField { id: apiBase; Layout.fillWidth: true; hint: "API Base（如 https://api.openai.com/v1）"; text: Bridge.apiState.base }
                    CmTextField { id: apiKey; Layout.fillWidth: true; hint: "API Key"; text: Bridge.apiState.key; echo: TextInput.Password }
                    CmTextField { id: apiModel; Layout.fillWidth: true; hint: "模型（如 gpt-4o-mini）"; text: Bridge.apiState.model }
                    PrimaryButton {
                        Layout.preferredWidth: 140
                        height: 40
                        radius: 20
                        text: "儲存 AI 設定"
                        onClicked: Bridge.saveApi(Bridge.apiState.enabled, apiBase.text, apiKey.text, apiModel.text)
                    }
                }
            }

            GlassCard {
                Layout.fillWidth: true
                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.s3
                    CmText { text: "後台運行"; font.pixelSize: 14; font.bold: true }
                    CmText {
                        Layout.fillWidth: true
                        text: "桌面版：關閉視窗會縮到系統匣繼續聆聽。\n安卓（OPPO/ColorOS）：首次使用請允許：通知、錄音、懸浮窗（顯示在其他應用上層）、自啟動與「電池不設限制」。詳細步驟見專案 android/README_OPPO_GUIDE.md。"
                        font.pixelSize: 12
                        color: Theme.textSecondary
                        wrapMode: Text.Wrap
                        lineHeight: 1.5
                    }
                }
            }

            GlassCard {
                Layout.fillWidth: true
                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.s3
                    CmText { text: "關於"; font.pixelSize: 14; font.bold: true }
                    CmText { Layout.fillWidth: true; text: "課堂智聽 ClassMate v1.1.0"; font.pixelSize: 12; color: Theme.textPrimary }
                    CmText {
                        Layout.fillWidth: true
                        text: "粵 · 英 · 普三語課堂監聽助手。問題偵測、點名提醒、熱詞知識庫與歷史紀錄均在本機離線運作；AI 接駁為可選增強。"
                        font.pixelSize: 11
                        color: Theme.textDim
                        wrapMode: Text.Wrap
                        lineHeight: 1.4
                    }
                    CmText {
                        Layout.fillWidth: true
                        text: "課程資料來源：澳門鏡湖護理學院 學士學位課程計劃（2025/2026 官網）"
                        font.pixelSize: 11
                        color: Theme.textDim
                        wrapMode: Text.Wrap
                        lineHeight: 1.4
                    }
                }
            }
        }
    }
}
