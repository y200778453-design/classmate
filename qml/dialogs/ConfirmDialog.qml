import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import ClassMateTheme
import "../components"

Dialog {
    id: dlg
    property string message: ""
    anchors.centerIn: Overlay.overlay
    width: Math.min(340, parent ? parent.width - 56 : 300)
    modal: true
    title: "確認"
    background: Rectangle { color: "#F7172338"; radius: Theme.rLg; border.color: Theme.border; border.width: 1 }
    contentItem: CmText { text: dlg.message; wrapMode: Text.Wrap; lineHeight: 1.4 }
    footer: DialogButtonBox {
        Button { text: "取消"; onClicked: dlg.reject() }
        Button {
            text: "確定"
            onClicked: dlg.accept()
            palette.button: Theme.danger
            palette.buttonText: "#FFFFFF"
        }
    }
}
