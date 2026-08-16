import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ClassMateTheme
import ClassMate.Core
import "../components"
import "../dialogs"

Item {
    id: page
    property var sel: null

    function refreshSel() {
        for (var i = 0; i < Bridge.subjects.length; i++) {
            if (Bridge.subjects[i].id === Bridge.currentSubjectId) {
                sel = Bridge.subjects[i]
                return
            }
        }
        sel = Bridge.subjects.length > 0 ? Bridge.subjects[0] : null
    }

    Component.onCompleted: refreshSel()

    Connections {
        target: Bridge
        function onSubjectsChanged() { page.refreshSel() }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.s5
        spacing: Theme.s4

        ColumnLayout {
            spacing: 2
            CmText { text: "科目與熱詞"; font.pixelSize: 24; font.bold: true }
            CmText { text: "大三 · 護理學學士 · 澳門鏡湖護理學院"; font.pixelSize: 12; color: Theme.textSecondary }
        }

        ListView {
            id: subjectList
            Layout.fillWidth: true
            Layout.preferredHeight: 104
            orientation: ListView.Horizontal
            spacing: 10
            clip: true
            model: Bridge.subjects
            delegate: SubjectCard {
                subject: modelData
                selected: modelData.id === Bridge.currentSubjectId
                onClicked: Bridge.selectSubject(modelData.id)
            }
        }

        GlassCard {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.s3

                RowLayout {
                    CmText { text: sel ? sel.icon : "✦"; font.pixelSize: 26 }
                    ColumnLayout {
                        spacing: 2
                        CmText {
                            Layout.fillWidth: true
                            text: sel ? sel.name : ""
                            font.pixelSize: 17
                            font.bold: true
                            elide: Text.ElideRight
                        }
                        CmText {
                            Layout.fillWidth: true
                            text: sel ? sel.nameEn : ""
                            font.pixelSize: 11
                            color: Theme.textDim
                            elide: Text.ElideRight
                        }
                    }
                    Item { Layout.fillWidth: true }
                    Rectangle {
                        Layout.preferredWidth: kindLabel.implicitWidth + 16
                        Layout.preferredHeight: 22
                        radius: 11
                        color: sel && sel.kind === "必修" ? "#2EFFB020" : "#2E9B6CFF"
                        CmText {
                            id: kindLabel
                            anchors.centerIn: parent
                            text: sel ? sel.kind : ""
                            font.pixelSize: 11
                            color: sel && sel.kind === "必修" ? Theme.warning : "#DCE4FF"
                        }
                    }
                }

                CmText {
                    Layout.fillWidth: true
                    text: "熱詞 " + (sel ? sel.hotwords.length : 0) + " 個 · 點擊查看重點 · 自訂詞可 ✕ 移除"
                    font.pixelSize: 11
                    color: Theme.textDim
                }

                ScrollView {
                    id: hotScroll
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    Flow {
                        id: hotFlow
                        width: hotScroll.availableWidth
                        spacing: 8
                        Repeater {
                            model: page.sel ? page.sel.hotwords : []
                            HotWordChip {
                                term: modelData.term
                                custom: !!modelData.custom
                                onClicked: hotDetail.show(modelData)
                                onRemoveRequested: Bridge.removeHotWord(page.sel.id, modelData.term)
                            }
                        }
                    }
                }

                PrimaryButton {
                    Layout.fillWidth: true
                    height: 44
                    radius: 22
                    text: "＋ 自訂熱詞"
                    color1: "#2E6C8CFF"
                    color2: "#2E9B6CFF"
                    onClicked: addDlg.openFor(page.sel.id, page.sel.name)
                }
            }
        }
    }

    HotWordDetail {
        id: hotDetail
        anchors.fill: parent
    }

    AddHotWordDialog { id: addDlg }
}
