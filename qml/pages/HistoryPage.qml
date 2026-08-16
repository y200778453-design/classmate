import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ClassMateTheme
import ClassMate.Core
import "../components"
import "../dialogs"

Item {
    id: page

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.s5
        spacing: Theme.s4

        RowLayout {
            ColumnLayout {
                spacing: 2
                CmText { text: "歷史紀錄"; font.pixelSize: 24; font.bold: true }
                CmText {
                    text: "今日 " + Bridge.stats.today + " · 共 " + Bridge.stats.total + " · 點名 " + Bridge.stats.nameCalls
                    font.pixelSize: 12
                    color: Theme.textSecondary
                }
            }
            Item { Layout.fillWidth: true }
            PrimaryButton {
                Layout.preferredWidth: 74
                height: 36
                radius: 18
                text: "匯出"
                color1: "#334C7CFF"
                color2: "#336C8CFF"
                onClicked: Bridge.exportHistory("")
            }
            PrimaryButton {
                Layout.preferredWidth: 74
                height: 36
                radius: 18
                text: "清空"
                color1: "#33485A75"
                color2: "#33343B66"
                onClicked: confirmDlg.open()
            }
        }

        CmTextField {
            id: searchField
            Layout.fillWidth: true
            hint: "搜尋問題 / 答案 / 科目…"
            onTextChanged: Bridge.searchHistory(text)
        }

        ListView {
            id: list
            objectName: "historyList"
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
            clip: true
            model: Bridge.historyModel
            delegate: HistoryCard {
                width: list.width
            }

            CmText {
                visible: list.count === 0
                anchors.centerIn: parent
                text: "尚無紀錄\n開始聆聽後，課堂問題與點名提醒會自動存檔"
                horizontalAlignment: Text.AlignHCenter
                color: Theme.textDim
                font.pixelSize: 13
            }
        }
    }

    ConfirmDialog {
        id: confirmDlg
        message: "確定清空全部歷史紀錄？此操作無法復原。"
        onAccepted: Bridge.clearHistory()
    }
}
