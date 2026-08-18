import QtQuick
import QtQuick.Controls
import ClassMateTheme
import ClassMate.Core
import "components"
import "pages"

ApplicationWindow {
    id: root
    width: 420
    height: 880
    minimumWidth: 340
    minimumHeight: 600
    visible: true
    title: "課堂智聽 ClassMate"
    color: Theme.bgTop

    property int pageIndex: 0

    function switchPage(i) {
        pageIndex = i
        navBar.current = i
        if (stack.currentItem !== pageComp(i).item)
            stack.replace(pageComp(i), {}, StackView.ReplaceTransition)
    }
    function pageComp(i) {
        return [listenPage, subjectsPage, historyPage, settingsPage][i]
    }

    // ---- animated background ----
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: Theme.bgTop }
            GradientStop { position: 1.0; color: Theme.bgBottom }
        }
    }
    Rectangle {
        id: blobA
        width: 380; height: 380; radius: 190
        x: -160; y: -120
        color: "#166C8CFF"
        opacity: 0.5
        NumberAnimation on opacity {
            running: true; loops: Animation.Infinite
            from: 0.35; to: 0.6; duration: 7200
            easing.type: Theme.easeInOut
        }
    }
    Rectangle {
        id: blobB
        width: 420; height: 420; radius: 210
        x: width * 0.45; y: height * 0.62
        color: "#149B6CFF"
        opacity: 0.5
        NumberAnimation on opacity {
            running: true; loops: Animation.Infinite
            from: 0.5; to: 0.3; duration: 8400
            easing.type: Theme.easeInOut
        }
    }

    // ---- pages ----
    StackView {
        id: stack
        objectName: "pageStack"
        anchors.fill: parent
        anchors.bottomMargin: 84
        clip: true
        initialItem: listenPage
        replaceEnter: Transition {
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: Theme.dBase; easing.type: Theme.easeOut }
            NumberAnimation { property: "x"; from: 60; to: 0; duration: Theme.dBase; easing.type: Theme.easeOut }
        }
        replaceExit: Transition {
            NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 150; easing.type: Theme.easeOut }
        }
    }
    Component { id: listenPage; ListenPage {} }
    Component { id: subjectsPage; SubjectsPage {} }
    Component { id: historyPage; HistoryPage {} }
    Component { id: settingsPage; SettingsPage {} }

    // ---- overlays ----
    Loader {
        id: alertLoader
        anchors.fill: parent
        z: 50
        active: true
        sourceComponent: AlertPopup {}
    }
    Loader {
        id: toastLoader
        anchors.fill: parent
        z: 60
        active: true
        sourceComponent: CmToast {}
    }

    NavBar {
        id: navBar
        z: 40
        onSelected: function(i) { root.switchPage(i) }
    }

    Connections {
        target: Bridge
        function onQuestionDetected(ev) { if (alertLoader.item) alertLoader.item.show(ev) }
        function onNameCalled(ev) { if (alertLoader.item) alertLoader.item.show(ev) }
        function onDemoCommand(cmd) {
            if (cmd === "page:subjects") root.switchPage(1)
            else if (cmd === "page:history") root.switchPage(2)
            else if (cmd === "page:settings") root.switchPage(3)
            else if (cmd === "page:listen") root.switchPage(0)
        }
        function onToast(t) { if (toastLoader.item) toastLoader.item.show(t.text, t.kind) }
    }
}
