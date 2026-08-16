import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import ClassMateTheme
import ClassMate.Core
import "../components"

Dialog {
    id: dlg
    property string subjectId: ""
    property string subjectName: ""
    anchors.centerIn: Overlay.overlay
    width: Math.min(360, parent ? parent.width - 48 : 320)
    modal: true
    title: "新增熱詞"
    background: Rectangle { color: "#F7172338"; radius: Theme.rLg; border.color: Theme.border; border.width: 1 }
    contentItem: ColumnLayout {
        spacing: Theme.s3
        CmText {
            Layout.fillWidth: true
            text: "加到「" + dlg.subjectName + "」的熱詞庫：課堂上出現此詞會加強識別，命中即以答題框架協助。"
            font.pixelSize: 12
            color: Theme.textSecondary
            wrapMode: Text.Wrap
            lineHeight: 1.4
        }
        CmTextField {
            id: input
            Layout.fillWidth: true
            hint: "例如：濕性敷料、造口袋更換"
        }
    }
    footer: DialogButtonBox {
        Button { text: "取消"; onClicked: dlg.reject() }
        Button {
            text: "加入"
            onClicked: dlg.accept()
            palette.button: Theme.accent
            palette.buttonText: "#FFFFFF"
        }
    }

    function openFor(id, name) {
        subjectId = id
        subjectName = name
        input.text = ""
        open()
    }

    onAccepted: {
        if (input.text.trim().length > 0)
            Bridge.addHotWord(subjectId, input.text.trim())
    }
}
