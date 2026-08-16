import QtQuick
import QtQuick.Layouts
import ClassMateTheme

GlassCard {
    id: root
    required property string tsText
    required property string subjectName
    required property string kindText
    required property string answer
    required property string modeText
    required property string lang
    required property string hotwordsText
    required property string questionText
    height: contentColumn.implicitHeight + 24

    ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        spacing: 6

        RowLayout {
            Rectangle {
                Layout.preferredWidth: kindBadge.implicitWidth + 16
                Layout.preferredHeight: 22
                radius: 11
                color: root.kindText.indexOf("點名") >= 0 ? "#59FF5C7A" : "#5935E0FF"
                CmText {
                    id: kindBadge
                    anchors.centerIn: parent
                    text: root.kindText
                    font.pixelSize: 11
                    font.bold: true
                    color: "#FFFFFF"
                }
            }
            CmText {
                Layout.fillWidth: true
                text: root.subjectName
                font.pixelSize: 12
                color: Theme.textSecondary
                elide: Text.ElideRight
            }
            CmText {
                text: root.tsText
                font.pixelSize: 11
                color: Theme.textDim
            }
        }

        CmText {
            Layout.fillWidth: true
            text: root.questionText
            font.pixelSize: 14
            font.bold: true
            wrapMode: Text.Wrap
            maximumLineCount: 2
            elide: Text.ElideRight
        }

        CmText {
            Layout.fillWidth: true
            text: root.answer
            font.pixelSize: 12
            color: Theme.textSecondary
            wrapMode: Text.Wrap
            maximumLineCount: 3
            elide: Text.ElideRight
        }

        RowLayout {
            CmText { text: root.modeText; font.pixelSize: 11; color: Theme.cyan }
            CmText { text: root.lang; font.pixelSize: 11; color: Theme.textDim }
            CmText {
                Layout.fillWidth: true
                text: root.hotwordsText
                font.pixelSize: 11
                color: Theme.warning
                elide: Text.ElideRight
            }
        }
    }
}
