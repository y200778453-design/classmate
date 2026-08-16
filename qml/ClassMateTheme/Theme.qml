pragma Singleton
import QtQuick

QtObject {
    // ---- palette (dark neon, tokens only — no hardcoded colors elsewhere) ----
    readonly property color bgTop: "#0A0F24"
    readonly property color bgBottom: "#171233"
    readonly property color card: "#12FFFFFF"
    readonly property color cardStrong: "#1CFFFFFF"
    readonly property color border: "#24FFFFFF"
    readonly property color textPrimary: "#F2F4FF"
    readonly property color textSecondary: "#9AA3C7"
    readonly property color textDim: "#5C6487"
    readonly property color accent: "#6C8CFF"
    readonly property color accent2: "#9B6CFF"
    readonly property color cyan: "#35E0FF"
    readonly property color success: "#3DDC97"
    readonly property color warning: "#FFB020"
    readonly property color danger: "#FF5C7A"
    readonly property color scrim: "#66000000"
    readonly property color popupBg: "#F01B2745"
    readonly property color popupUrgentBg: "#F02B1E3F"

    // ---- radius scale ----
    readonly property int rSm: 12
    readonly property int rMd: 16
    readonly property int rLg: 20
    readonly property int rXl: 24
    readonly property int rPill: 999

    // ---- spacing (8px grid) ----
    readonly property int s1: 4
    readonly property int s2: 8
    readonly property int s3: 12
    readonly property int s4: 16
    readonly property int s5: 20
    readonly property int s6: 24
    readonly property int s8: 32

    // ---- easing tokens (motion framework table) ----
    readonly property int easeOut: Easing.OutCubic
    readonly property int easeInOut: Easing.InOutCubic
    readonly property int easeBack: Easing.OutBack
    readonly property int easeLinear: Easing.Linear

    // ---- durations ----
    readonly property int dFast: 120
    readonly property int dBase: 200
    readonly property int dPopup: 260
    readonly property int dSwitch: 260

    readonly property string fontFamily: Qt.platform.os === "android" ? "" : "Microsoft YaHei UI"
}
