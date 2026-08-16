import QtQuick
import QtQuick.Controls.Basic
import ClassMateTheme

TextField {
    id: root
    property string hint: ""
    property int echo: TextInput.Normal
    echoMode: root.echo
    font.family: Theme.fontFamily
    font.pixelSize: 14
    color: Theme.textPrimary
    placeholderText: hint
    placeholderTextColor: Theme.textDim
    leftPadding: 14
    rightPadding: 14
    topPadding: 12
    bottomPadding: 12
    background: Rectangle {
        radius: Theme.rSm
        color: "#14FFFFFF"
        border.width: 1
        border.color: root.activeFocus ? Theme.accent : Theme.border
    }
}
