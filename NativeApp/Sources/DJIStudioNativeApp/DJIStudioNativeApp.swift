import SwiftUI
import AppKit
import UniformTypeIdentifiers

@main
struct DJIStudioNativeApp: App {
    @StateObject private var viewModel = ExportViewModel()

    var body: some Scene {
        WindowGroup {
            ContentView(viewModel: viewModel)
                .frame(minWidth: 1120, minHeight: 840)
        }
    }
}

enum ExportPreset: String, CaseIterable, Identifiable {
    case sixK = "6K"
    case eightK = "8K"

    var id: String { rawValue }

    var resolutionType: String {
        switch self {
        case .sixK: return "12"
        case .eightK: return "14"
        }
    }
}

enum FrameRateOption: String, CaseIterable, Identifiable {
    case source = "source"
    case fps24 = "24"
    case fps25 = "25"
    case fps30 = "30"
    case fps50 = "50"
    case fps60 = "60"

    var id: String { rawValue }

    var frameRateValue: String? {
        switch self {
        case .source: return nil
        case .fps24: return "24"
        case .fps25: return "25"
        case .fps30: return "30"
        case .fps50: return "50"
        case .fps60: return "60"
        }
    }
}

enum BitrateModeOption: String, CaseIterable, Identifiable {
    case low
    case medium
    case high
    case custom

    var id: String { rawValue }
}

enum DenoiseModeOption: String, CaseIterable, Identifiable {
    case performance
    case quality

    var id: String { rawValue }
}

enum AppLanguage: String, CaseIterable, Identifiable {
    case system = "system"
    case english = "en"
    case simplifiedChinese = "zh-Hans"
    case traditionalChinese = "zh-Hant"
    case japanese = "ja"
    case korean = "ko"
    case french = "fr"
    case german = "de"
    case spanish = "es"
    case portugueseBrazil = "pt-BR"
    case russian = "ru"
    case italian = "it"
    case arabic = "ar"

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .system: return "System"
        case .english: return "English"
        case .simplifiedChinese: return "中文(简体)"
        case .traditionalChinese: return "中文(繁體)"
        case .japanese: return "日本語"
        case .korean: return "한국어"
        case .french: return "Français"
        case .german: return "Deutsch"
        case .spanish: return "Español"
        case .portugueseBrazil: return "Português (Brasil)"
        case .russian: return "Русский"
        case .italian: return "Italiano"
        case .arabic: return "العربية"
        }
    }

    var localeIdentifier: String {
        switch self {
        case .system:
            return Locale.preferredLanguages.first ?? "en"
        default:
            return rawValue
        }
    }

    static func resolvedDefault() -> AppLanguage {
        let preferred = Locale.preferredLanguages.first ?? "en"
        if preferred.hasPrefix("zh-Hant") || preferred.hasPrefix("zh-TW") || preferred.hasPrefix("zh-HK") {
            return .traditionalChinese
        }
        if preferred.hasPrefix("zh") { return .simplifiedChinese }
        if preferred.hasPrefix("ja") { return .japanese }
        if preferred.hasPrefix("ko") { return .korean }
        if preferred.hasPrefix("fr") { return .french }
        if preferred.hasPrefix("de") { return .german }
        if preferred.hasPrefix("es") { return .spanish }
        if preferred.hasPrefix("pt") { return .portugueseBrazil }
        if preferred.hasPrefix("ru") { return .russian }
        if preferred.hasPrefix("it") { return .italian }
        if preferred.hasPrefix("ar") { return .arabic }
        return .english
    }
}

enum LKey: String {
    case appTitle
    case language
    case osvFiles
    case dragFilesHere
    case orUseAddFiles
    case exportSettings
    case preset
    case cleanupTemporaryProjects
    case outputDirectory
    case notSelected
    case chooseOutput
    case reveal
    case clear
    case running
    case startExport
    case stop
    case queuedFiles
    case runLog
    case noOutputYet
    case lastRun
    case lastRunSummary
    case errorsSummary
    case ready
    case noOSVFilesSelected
    case noOutputDirectorySelected
    case runningExport
    case exportFinished
    case exportStopped
    case exportFinishedWithErrors
    case failedToLaunchExport
    case stoppingExport
    case manifest
    case selectedFiles
    case nativeAppNote
    case clickToChooseFiles
    case frameRate
    case sourceFrameRate
    case bitrate
    case low
    case medium
    case high
    case custom
    case customBitrateMbps
    case denoise
    case denoiseMode
    case performancePriority
    case qualityPriority
    case tenBit
    case parallelCount
    case progress
    case queuedFilesTitle
    case statePending
    case statePrepared
    case stateQueued
    case stateRunning
    case stateFinished
    case stateError
    case batchHint
}

enum L10n {
    static let fallback: [LKey: String] = [
        .appTitle: "DJIStudio Native Export",
        .language: "Language",
        .osvFiles: "OSV Files",
        .dragFilesHere: "Drag OSV files here",
        .orUseAddFiles: "or use Add Files",
        .exportSettings: "Export Settings",
        .preset: "Preset",
        .cleanupTemporaryProjects: "Cleanup temporary projects after export",
        .outputDirectory: "Output Directory",
        .notSelected: "Not selected",
        .chooseOutput: "Choose Output",
        .reveal: "Reveal",
        .clear: "Clear",
        .running: "Running...",
        .startExport: "Start Export",
        .stop: "Stop",
        .queuedFiles: "Queued Files (%@)",
        .runLog: "Run Log",
        .noOutputYet: "No output yet",
        .lastRun: "Last Run",
        .lastRunSummary: "Files: %@  Temp projects: %@  Cleanup steps: %@",
        .errorsSummary: "Errors: %@",
        .ready: "Ready",
        .noOSVFilesSelected: "No OSV files selected",
        .noOutputDirectorySelected: "No output directory selected",
        .runningExport: "Running export...",
        .exportFinished: "Export finished",
        .exportStopped: "Export stopped",
        .exportFinishedWithErrors: "Export finished with errors (%@)",
        .failedToLaunchExport: "Failed to launch export: %@",
        .stoppingExport: "Stopping export...",
        .manifest: "Manifest: %@",
        .selectedFiles: "Selected files must end with .OSV",
        .nativeAppNote: "Swift UI front-end, validated Python export backend.",
        .clickToChooseFiles: "or click the box to choose files",
        .frameRate: "Frame Rate",
        .sourceFrameRate: "Use source fps",
        .bitrate: "Bitrate",
        .low: "Low",
        .medium: "Medium",
        .high: "High",
        .custom: "Custom",
        .customBitrateMbps: "Custom bitrate (Mbps)",
        .denoise: "Denoise",
        .denoiseMode: "Denoise Mode",
        .performancePriority: "Performance priority",
        .qualityPriority: "Quality priority",
        .tenBit: "10-Bit",
        .parallelCount: "Parallel Count",
        .progress: "Progress",
        .queuedFilesTitle: "Queued Files",
        .statePending: "Pending",
        .statePrepared: "Prepared",
        .stateQueued: "Queued",
        .stateRunning: "Running",
        .stateFinished: "Finished",
        .stateError: "Error",
        .batchHint: "Parallel count controls how many files are staged into one export batch."
    ]

    static let translations: [AppLanguage: [LKey: String]] = [
        .english: fallback,
        .simplifiedChinese: [
            .appTitle: "DJIStudio 原生导出",
            .language: "语言",
            .osvFiles: "OSV 文件",
            .dragFilesHere: "把 OSV 文件拖到这里",
            .orUseAddFiles: "或点击“添加文件”",
            .exportSettings: "导出设置",
            .preset: "预设",
            .cleanupTemporaryProjects: "导出完成后清理临时项目",
            .outputDirectory: "输出目录",
            .notSelected: "未选择",
            .chooseOutput: "选择输出目录",
            .reveal: "显示",
            .clear: "清空",
            .running: "运行中...",
            .startExport: "开始导出",
            .stop: "停止",
            .queuedFiles: "待导出文件（%@）",
            .runLog: "运行日志",
            .noOutputYet: "暂无输出",
            .lastRun: "最近一次运行",
            .lastRunSummary: "文件数：%@  临时项目：%@  清理步骤：%@",
            .errorsSummary: "错误：%@",
            .ready: "就绪",
            .noOSVFilesSelected: "还没有选择 OSV 文件",
            .noOutputDirectorySelected: "还没有选择输出目录",
            .runningExport: "正在导出...",
            .exportFinished: "导出完成",
            .exportStopped: "导出已停止",
            .exportFinishedWithErrors: "导出结束，但有错误（%@）",
            .failedToLaunchExport: "启动导出失败：%@",
            .stoppingExport: "正在停止导出...",
            .manifest: "清单文件：%@",
            .selectedFiles: "所选文件必须以 .OSV 结尾",
            .nativeAppNote: "Swift 原生界面，复用已验证的 Python 导出后端。",
            .clickToChooseFiles: "或点击框框选择文件",
            .frameRate: "帧率",
            .sourceFrameRate: "跟随源文件",
            .bitrate: "码率",
            .low: "低",
            .medium: "中",
            .high: "高",
            .custom: "自定义",
            .customBitrateMbps: "自定义码率（Mbps）",
            .denoise: "画面降噪",
            .denoiseMode: "降噪模式",
            .performancePriority: "性能优先",
            .qualityPriority: "效果优先",
            .tenBit: "10-Bit",
            .parallelCount: "并行数量",
            .progress: "进度",
            .statePending: "待处理",
            .statePrepared: "已准备",
            .stateQueued: "排队中",
            .stateRunning: "导出中",
            .stateFinished: "已完成",
            .stateError: "错误",
            .batchHint: "并行数量控制每一批次预先排入导出队列的文件数。"
        ],
        .traditionalChinese: [
            .appTitle: "DJIStudio 原生匯出",
            .language: "語言",
            .osvFiles: "OSV 檔案",
            .dragFilesHere: "把 OSV 檔案拖到這裡",
            .orUseAddFiles: "或點選「新增檔案」",
            .exportSettings: "匯出設定",
            .preset: "預設",
            .cleanupTemporaryProjects: "匯出完成後清理暫存專案",
            .outputDirectory: "輸出資料夾",
            .notSelected: "未選擇",
            .chooseOutput: "選擇輸出資料夾",
            .reveal: "顯示",
            .clear: "清空",
            .running: "執行中...",
            .startExport: "開始匯出",
            .stop: "停止",
            .queuedFiles: "待匯出檔案（%@）",
            .runLog: "執行日誌",
            .noOutputYet: "尚無輸出",
            .lastRun: "最近一次執行",
            .lastRunSummary: "檔案數：%@  暫存專案：%@  清理步驟：%@",
            .errorsSummary: "錯誤：%@",
            .ready: "就緒",
            .noOSVFilesSelected: "尚未選擇 OSV 檔案",
            .noOutputDirectorySelected: "尚未選擇輸出資料夾",
            .runningExport: "正在匯出...",
            .exportFinished: "匯出完成",
            .exportStopped: "匯出已停止",
            .exportFinishedWithErrors: "匯出結束，但有錯誤（%@）",
            .failedToLaunchExport: "啟動匯出失敗：%@",
            .stoppingExport: "正在停止匯出...",
            .manifest: "清單檔案：%@",
            .selectedFiles: "選擇的檔案必須以 .OSV 結尾",
            .nativeAppNote: "Swift 原生介面，重用已驗證的 Python 匯出後端。",
            .clickToChooseFiles: "或點擊框框選擇檔案",
            .frameRate: "幀率",
            .sourceFrameRate: "跟隨來源檔案",
            .bitrate: "位元率",
            .low: "低",
            .medium: "中",
            .high: "高",
            .custom: "自訂",
            .customBitrateMbps: "自訂位元率（Mbps）",
            .denoise: "畫面降噪",
            .denoiseMode: "降噪模式",
            .performancePriority: "效能優先",
            .qualityPriority: "效果優先",
            .tenBit: "10-Bit",
            .parallelCount: "並行數量",
            .progress: "進度",
            .statePending: "待處理",
            .statePrepared: "已準備",
            .stateQueued: "排隊中",
            .stateRunning: "匯出中",
            .stateFinished: "已完成",
            .stateError: "錯誤",
            .batchHint: "並行數量控制每一批次預先排入匯出佇列的檔案數。"
        ],
        .japanese: [
            .appTitle: "DJIStudio ネイティブ書き出し",
            .language: "言語",
            .osvFiles: "OSV ファイル",
            .dragFilesHere: "OSV ファイルをここにドラッグ",
            .orUseAddFiles: "または「ファイル追加」を使用",
            .exportSettings: "書き出し設定",
            .preset: "プリセット",
            .cleanupTemporaryProjects: "書き出し後に一時プロジェクトを削除",
            .outputDirectory: "出力フォルダ",
            .notSelected: "未選択",
            .chooseOutput: "出力先を選択",
            .reveal: "表示",
            .clear: "クリア",
            .running: "実行中...",
            .startExport: "書き出し開始",
            .stop: "停止",
            .queuedFiles: "キュー中のファイル（%@）",
            .runLog: "実行ログ",
            .noOutputYet: "まだ出力はありません",
            .lastRun: "前回の実行",
            .lastRunSummary: "ファイル数: %@  一時プロジェクト: %@  クリーンアップ: %@",
            .errorsSummary: "エラー: %@",
            .ready: "準備完了",
            .noOSVFilesSelected: "OSV ファイルが選択されていません",
            .noOutputDirectorySelected: "出力フォルダが選択されていません",
            .runningExport: "書き出し中...",
            .exportFinished: "書き出し完了",
            .exportStopped: "書き出しを停止しました",
            .exportFinishedWithErrors: "書き出しは完了しましたがエラーがあります（%@）",
            .failedToLaunchExport: "書き出し開始に失敗しました: %@",
            .stoppingExport: "書き出しを停止しています...",
            .manifest: "マニフェスト: %@",
            .selectedFiles: "選択ファイルは .OSV で終わる必要があります",
            .nativeAppNote: "Swift ネイティブ UI、検証済み Python 書き出しバックエンド。",
            .clickToChooseFiles: "または枠をクリックしてファイルを選択",
            .frameRate: "フレームレート",
            .sourceFrameRate: "ソース fps を使用",
            .bitrate: "ビットレート",
            .low: "低",
            .medium: "中",
            .high: "高",
            .custom: "カスタム",
            .customBitrateMbps: "カスタムビットレート（Mbps）",
            .denoise: "ノイズ除去",
            .denoiseMode: "ノイズ除去モード",
            .performancePriority: "性能優先",
            .qualityPriority: "画質優先",
            .tenBit: "10-Bit",
            .parallelCount: "並列数",
            .progress: "進捗",
            .statePending: "保留",
            .statePrepared: "準備完了",
            .stateQueued: "待機中",
            .stateRunning: "実行中",
            .stateFinished: "完了",
            .stateError: "エラー",
            .batchHint: "並列数は 1 バッチで先に投入するファイル数を制御します。"
        ],
        .korean: [
            .appTitle: "DJIStudio 네이티브 내보내기",
            .language: "언어",
            .osvFiles: "OSV 파일",
            .dragFilesHere: "여기로 OSV 파일을 드래그하세요",
            .orUseAddFiles: "또는 파일 추가를 사용하세요",
            .exportSettings: "내보내기 설정",
            .preset: "프리셋",
            .cleanupTemporaryProjects: "내보내기 후 임시 프로젝트 정리",
            .outputDirectory: "출력 폴더",
            .notSelected: "선택되지 않음",
            .chooseOutput: "출력 폴더 선택",
            .reveal: "보기",
            .clear: "지우기",
            .running: "실행 중...",
            .startExport: "내보내기 시작",
            .stop: "중지",
            .queuedFiles: "대기 중 파일 (%@)",
            .runLog: "실행 로그",
            .noOutputYet: "아직 출력 없음",
            .lastRun: "최근 실행",
            .lastRunSummary: "파일: %@  임시 프로젝트: %@  정리 단계: %@",
            .errorsSummary: "오류: %@",
            .ready: "준비 완료",
            .noOSVFilesSelected: "선택된 OSV 파일이 없습니다",
            .noOutputDirectorySelected: "출력 폴더가 선택되지 않았습니다",
            .runningExport: "내보내는 중...",
            .exportFinished: "내보내기 완료",
            .exportStopped: "내보내기를 중지했습니다",
            .exportFinishedWithErrors: "내보내기가 끝났지만 오류가 있습니다 (%@)",
            .failedToLaunchExport: "내보내기 시작 실패: %@",
            .stoppingExport: "내보내기 중지 중...",
            .manifest: "매니페스트: %@",
            .selectedFiles: "선택한 파일은 .OSV 여야 합니다",
            .nativeAppNote: "Swift 네이티브 UI, 검증된 Python 내보내기 백엔드 사용.",
            .clickToChooseFiles: "또는 상자를 클릭해 파일 선택",
            .frameRate: "프레임레이트",
            .sourceFrameRate: "원본 fps 사용",
            .bitrate: "비트레이트",
            .low: "낮음",
            .medium: "중간",
            .high: "높음",
            .custom: "사용자 지정",
            .customBitrateMbps: "사용자 지정 비트레이트 (Mbps)",
            .denoise: "노이즈 제거",
            .denoiseMode: "노이즈 제거 모드",
            .performancePriority: "성능 우선",
            .qualityPriority: "화질 우선",
            .tenBit: "10-Bit",
            .parallelCount: "병렬 수",
            .progress: "진행률",
            .statePending: "대기",
            .statePrepared: "준비됨",
            .stateQueued: "대기열",
            .stateRunning: "실행 중",
            .stateFinished: "완료",
            .stateError: "오류",
            .batchHint: "병렬 수는 한 배치에 미리 넣는 파일 수를 제어합니다."
        ],
        .french: [
            .appTitle: "Export natif DJIStudio",
            .language: "Langue",
            .osvFiles: "Fichiers OSV",
            .dragFilesHere: "Glissez les fichiers OSV ici",
            .orUseAddFiles: "ou utilisez Ajouter des fichiers",
            .exportSettings: "Paramètres d’export",
            .preset: "Préréglage",
            .cleanupTemporaryProjects: "Supprimer les projets temporaires après l’export",
            .outputDirectory: "Dossier de sortie",
            .notSelected: "Non sélectionné",
            .chooseOutput: "Choisir le dossier",
            .reveal: "Afficher",
            .clear: "Effacer",
            .running: "En cours...",
            .startExport: "Lancer l’export",
            .stop: "Arrêter",
            .queuedFiles: "Fichiers en file (%@)",
            .runLog: "Journal d’exécution",
            .noOutputYet: "Aucune sortie pour le moment",
            .lastRun: "Dernière exécution",
            .lastRunSummary: "Fichiers : %@  Projets temporaires : %@  Étapes de nettoyage : %@",
            .errorsSummary: "Erreurs : %@",
            .ready: "Prêt",
            .noOSVFilesSelected: "Aucun fichier OSV sélectionné",
            .noOutputDirectorySelected: "Aucun dossier de sortie sélectionné",
            .runningExport: "Export en cours...",
            .exportFinished: "Export terminé",
            .exportFinishedWithErrors: "Export terminé avec des erreurs (%@)",
            .failedToLaunchExport: "Échec du démarrage de l’export : %@",
            .stoppingExport: "Arrêt de l’export...",
            .manifest: "Manifeste : %@",
            .selectedFiles: "Les fichiers sélectionnés doivent se terminer par .OSV",
            .nativeAppNote: "Interface Swift native, backend d’export Python validé.",
            .clickToChooseFiles: "ou cliquez dans la zone pour choisir des fichiers",
            .frameRate: "Fréquence d’images",
            .sourceFrameRate: "Utiliser le fps source",
            .bitrate: "Débit",
            .low: "Bas",
            .medium: "Moyen",
            .high: "Élevé",
            .custom: "Personnalisé",
            .customBitrateMbps: "Débit personnalisé (Mbps)",
            .denoise: "Réduction du bruit",
            .denoiseMode: "Mode de réduction du bruit",
            .performancePriority: "Priorité aux performances",
            .qualityPriority: "Priorité à la qualité",
            .tenBit: "10-Bit",
            .parallelCount: "Nombre parallèle",
            .progress: "Progression",
            .statePending: "En attente",
            .statePrepared: "Préparé",
            .stateQueued: "En file",
            .stateRunning: "En cours",
            .stateFinished: "Terminé",
            .stateError: "Erreur",
            .batchHint: "Le nombre parallèle contrôle combien de fichiers sont ajoutés à une même vague d’export."
        ],
        .german: [
            .appTitle: "DJIStudio Native-Export",
            .language: "Sprache",
            .osvFiles: "OSV-Dateien",
            .dragFilesHere: "OSV-Dateien hierher ziehen",
            .orUseAddFiles: "oder Dateien hinzufügen verwenden",
            .exportSettings: "Exporteinstellungen",
            .preset: "Voreinstellung",
            .cleanupTemporaryProjects: "Temporäre Projekte nach Export löschen",
            .outputDirectory: "Ausgabeordner",
            .notSelected: "Nicht ausgewählt",
            .chooseOutput: "Ausgabe wählen",
            .reveal: "Anzeigen",
            .clear: "Leeren",
            .running: "Läuft...",
            .startExport: "Export starten",
            .stop: "Stopp",
            .queuedFiles: "Dateien in Warteschlange (%@)",
            .runLog: "Protokoll",
            .noOutputYet: "Noch keine Ausgabe",
            .lastRun: "Letzter Lauf",
            .lastRunSummary: "Dateien: %@  Temporäre Projekte: %@  Bereinigungsschritte: %@",
            .errorsSummary: "Fehler: %@",
            .ready: "Bereit",
            .noOSVFilesSelected: "Keine OSV-Dateien ausgewählt",
            .noOutputDirectorySelected: "Kein Ausgabeordner ausgewählt",
            .runningExport: "Export läuft...",
            .exportFinished: "Export abgeschlossen",
            .exportFinishedWithErrors: "Export mit Fehlern abgeschlossen (%@)",
            .failedToLaunchExport: "Exportstart fehlgeschlagen: %@",
            .stoppingExport: "Export wird gestoppt...",
            .manifest: "Manifest: %@",
            .selectedFiles: "Ausgewählte Dateien müssen auf .OSV enden",
            .nativeAppNote: "Native Swift-Oberfläche mit validiertem Python-Export-Backend.",
            .clickToChooseFiles: "oder klicken Sie in die Fläche, um Dateien auszuwählen",
            .frameRate: "Bildrate",
            .sourceFrameRate: "Quell-fps verwenden",
            .bitrate: "Bitrate",
            .low: "Niedrig",
            .medium: "Mittel",
            .high: "Hoch",
            .custom: "Benutzerdefiniert",
            .customBitrateMbps: "Benutzerdefinierte Bitrate (Mbps)",
            .denoise: "Rauschminderung",
            .denoiseMode: "Rauschminderungsmodus",
            .performancePriority: "Leistung bevorzugen",
            .qualityPriority: "Qualität bevorzugen",
            .tenBit: "10-Bit",
            .parallelCount: "Parallelzahl",
            .progress: "Fortschritt",
            .statePending: "Ausstehend",
            .statePrepared: "Vorbereitet",
            .stateQueued: "In Warteschlange",
            .stateRunning: "Läuft",
            .stateFinished: "Abgeschlossen",
            .stateError: "Fehler",
            .batchHint: "Die Parallelzahl steuert, wie viele Dateien pro Exportwelle vorgemerkt werden."
        ],
        .spanish: [
            .appTitle: "Exportación nativa DJIStudio",
            .language: "Idioma",
            .osvFiles: "Archivos OSV",
            .dragFilesHere: "Arrastra archivos OSV aquí",
            .orUseAddFiles: "o usa Agregar archivos",
            .exportSettings: "Configuración de exportación",
            .preset: "Preajuste",
            .cleanupTemporaryProjects: "Eliminar proyectos temporales después de exportar",
            .outputDirectory: "Directorio de salida",
            .notSelected: "No seleccionado",
            .chooseOutput: "Elegir salida",
            .reveal: "Mostrar",
            .clear: "Limpiar",
            .running: "En ejecución...",
            .startExport: "Iniciar exportación",
            .stop: "Detener",
            .queuedFiles: "Archivos en cola (%@)",
            .runLog: "Registro de ejecución",
            .noOutputYet: "Sin salida todavía",
            .lastRun: "Última ejecución",
            .lastRunSummary: "Archivos: %@  Proyectos temporales: %@  Pasos de limpieza: %@",
            .errorsSummary: "Errores: %@",
            .ready: "Listo",
            .noOSVFilesSelected: "No hay archivos OSV seleccionados",
            .noOutputDirectorySelected: "No se ha seleccionado un directorio de salida",
            .runningExport: "Exportando...",
            .exportFinished: "Exportación finalizada",
            .exportFinishedWithErrors: "La exportación terminó con errores (%@)",
            .failedToLaunchExport: "No se pudo iniciar la exportación: %@",
            .stoppingExport: "Deteniendo exportación...",
            .manifest: "Manifiesto: %@",
            .selectedFiles: "Los archivos seleccionados deben terminar en .OSV",
            .nativeAppNote: "Interfaz nativa en Swift, backend Python de exportación validado.",
            .clickToChooseFiles: "o haz clic en el cuadro para elegir archivos",
            .frameRate: "Fotogramas",
            .sourceFrameRate: "Usar fps de origen",
            .bitrate: "Bitrate",
            .low: "Bajo",
            .medium: "Medio",
            .high: "Alto",
            .custom: "Personalizado",
            .customBitrateMbps: "Bitrate personalizado (Mbps)",
            .denoise: "Reducción de ruido",
            .denoiseMode: "Modo de reducción de ruido",
            .performancePriority: "Prioridad al rendimiento",
            .qualityPriority: "Prioridad a la calidad",
            .tenBit: "10-Bit",
            .parallelCount: "Cantidad paralela",
            .progress: "Progreso",
            .statePending: "Pendiente",
            .statePrepared: "Preparado",
            .stateQueued: "En cola",
            .stateRunning: "En ejecución",
            .stateFinished: "Finalizado",
            .stateError: "Error",
            .batchHint: "La cantidad paralela controla cuántos archivos se ponen por adelantado en cada lote de exportación."
        ],
        .portugueseBrazil: [
            .appTitle: "Exportação nativa DJIStudio",
            .language: "Idioma",
            .osvFiles: "Arquivos OSV",
            .dragFilesHere: "Arraste arquivos OSV aqui",
            .orUseAddFiles: "ou use Adicionar arquivos",
            .exportSettings: "Configurações de exportação",
            .preset: "Predefinição",
            .cleanupTemporaryProjects: "Limpar projetos temporários após a exportação",
            .outputDirectory: "Diretório de saída",
            .notSelected: "Não selecionado",
            .chooseOutput: "Escolher saída",
            .reveal: "Mostrar",
            .clear: "Limpar",
            .running: "Executando...",
            .startExport: "Iniciar exportação",
            .stop: "Parar",
            .queuedFiles: "Arquivos na fila (%@)",
            .runLog: "Log de execução",
            .noOutputYet: "Sem saída ainda",
            .lastRun: "Última execução",
            .lastRunSummary: "Arquivos: %@  Projetos temporários: %@  Etapas de limpeza: %@",
            .errorsSummary: "Erros: %@",
            .ready: "Pronto",
            .noOSVFilesSelected: "Nenhum arquivo OSV selecionado",
            .noOutputDirectorySelected: "Nenhum diretório de saída selecionado",
            .runningExport: "Exportando...",
            .exportFinished: "Exportação concluída",
            .exportFinishedWithErrors: "A exportação terminou com erros (%@)",
            .failedToLaunchExport: "Falha ao iniciar a exportação: %@",
            .stoppingExport: "Parando exportação...",
            .manifest: "Manifesto: %@",
            .selectedFiles: "Os arquivos selecionados devem terminar com .OSV",
            .nativeAppNote: "Interface Swift nativa com backend Python de exportação validado.",
            .clickToChooseFiles: "ou clique na área para escolher arquivos",
            .frameRate: "Taxa de quadros",
            .sourceFrameRate: "Usar fps da origem",
            .bitrate: "Bitrate",
            .low: "Baixo",
            .medium: "Médio",
            .high: "Alto",
            .custom: "Personalizado",
            .customBitrateMbps: "Bitrate personalizado (Mbps)",
            .denoise: "Redução de ruído",
            .denoiseMode: "Modo de redução de ruído",
            .performancePriority: "Prioridade ao desempenho",
            .qualityPriority: "Prioridade à qualidade",
            .tenBit: "10-Bit",
            .parallelCount: "Quantidade paralela",
            .progress: "Progresso",
            .statePending: "Pendente",
            .statePrepared: "Preparado",
            .stateQueued: "Na fila",
            .stateRunning: "Em execução",
            .stateFinished: "Concluído",
            .stateError: "Erro",
            .batchHint: "A quantidade paralela controla quantos arquivos entram em cada lote de exportação."
        ],
        .russian: [
            .appTitle: "Нативный экспорт DJIStudio",
            .language: "Язык",
            .osvFiles: "Файлы OSV",
            .dragFilesHere: "Перетащите файлы OSV сюда",
            .orUseAddFiles: "или используйте Добавить файлы",
            .exportSettings: "Параметры экспорта",
            .preset: "Профиль",
            .cleanupTemporaryProjects: "Удалять временные проекты после экспорта",
            .outputDirectory: "Папка вывода",
            .notSelected: "Не выбрано",
            .chooseOutput: "Выбрать папку",
            .reveal: "Показать",
            .clear: "Очистить",
            .running: "Выполняется...",
            .startExport: "Начать экспорт",
            .stop: "Остановить",
            .queuedFiles: "Файлы в очереди (%@)",
            .runLog: "Журнал выполнения",
            .noOutputYet: "Вывода пока нет",
            .lastRun: "Последний запуск",
            .lastRunSummary: "Файлы: %@  Временные проекты: %@  Шаги очистки: %@",
            .errorsSummary: "Ошибки: %@",
            .ready: "Готово",
            .noOSVFilesSelected: "Файлы OSV не выбраны",
            .noOutputDirectorySelected: "Папка вывода не выбрана",
            .runningExport: "Экспорт выполняется...",
            .exportFinished: "Экспорт завершён",
            .exportFinishedWithErrors: "Экспорт завершён с ошибками (%@)",
            .failedToLaunchExport: "Не удалось запустить экспорт: %@",
            .stoppingExport: "Остановка экспорта...",
            .manifest: "Манифест: %@",
            .selectedFiles: "Выбранные файлы должны оканчиваться на .OSV",
            .nativeAppNote: "Нативный интерфейс на Swift, проверенный Python-бэкенд экспорта.",
            .clickToChooseFiles: "или нажмите на область, чтобы выбрать файлы",
            .frameRate: "Частота кадров",
            .sourceFrameRate: "Использовать fps исходника",
            .bitrate: "Битрейт",
            .low: "Низкий",
            .medium: "Средний",
            .high: "Высокий",
            .custom: "Пользовательский",
            .customBitrateMbps: "Пользовательский битрейт (Mbps)",
            .denoise: "Шумоподавление",
            .denoiseMode: "Режим шумоподавления",
            .performancePriority: "Приоритет производительности",
            .qualityPriority: "Приоритет качества",
            .tenBit: "10-Bit",
            .parallelCount: "Параллельность",
            .progress: "Прогресс",
            .statePending: "Ожидание",
            .statePrepared: "Подготовлено",
            .stateQueued: "В очереди",
            .stateRunning: "Выполняется",
            .stateFinished: "Завершено",
            .stateError: "Ошибка",
            .batchHint: "Параллельность управляет числом файлов, заранее поставленных в одну волну экспорта."
        ],
        .italian: [
            .appTitle: "Esportazione nativa DJIStudio",
            .language: "Lingua",
            .osvFiles: "File OSV",
            .dragFilesHere: "Trascina qui i file OSV",
            .orUseAddFiles: "oppure usa Aggiungi file",
            .exportSettings: "Impostazioni di esportazione",
            .preset: "Preset",
            .cleanupTemporaryProjects: "Pulisci i progetti temporanei dopo l’esportazione",
            .outputDirectory: "Cartella di output",
            .notSelected: "Non selezionato",
            .chooseOutput: "Scegli output",
            .reveal: "Mostra",
            .clear: "Cancella",
            .running: "In esecuzione...",
            .startExport: "Avvia esportazione",
            .stop: "Ferma",
            .queuedFiles: "File in coda (%@)",
            .runLog: "Log di esecuzione",
            .noOutputYet: "Nessun output al momento",
            .lastRun: "Ultima esecuzione",
            .lastRunSummary: "File: %@  Progetti temporanei: %@  Passaggi di pulizia: %@",
            .errorsSummary: "Errori: %@",
            .ready: "Pronto",
            .noOSVFilesSelected: "Nessun file OSV selezionato",
            .noOutputDirectorySelected: "Nessuna cartella di output selezionata",
            .runningExport: "Esportazione in corso...",
            .exportFinished: "Esportazione completata",
            .exportFinishedWithErrors: "Esportazione completata con errori (%@)",
            .failedToLaunchExport: "Avvio esportazione non riuscito: %@",
            .stoppingExport: "Arresto esportazione...",
            .manifest: "Manifest: %@",
            .selectedFiles: "I file selezionati devono terminare con .OSV",
            .nativeAppNote: "Interfaccia Swift nativa, backend Python di esportazione validato.",
            .clickToChooseFiles: "oppure fai clic nell’area per scegliere i file",
            .frameRate: "Frame rate",
            .sourceFrameRate: "Usa fps sorgente",
            .bitrate: "Bitrate",
            .low: "Basso",
            .medium: "Medio",
            .high: "Alto",
            .custom: "Personalizzato",
            .customBitrateMbps: "Bitrate personalizzato (Mbps)",
            .denoise: "Riduzione rumore",
            .denoiseMode: "Modalità riduzione rumore",
            .performancePriority: "Priorità prestazioni",
            .qualityPriority: "Priorità qualità",
            .tenBit: "10-Bit",
            .parallelCount: "Numero parallelo",
            .progress: "Avanzamento",
            .statePending: "In attesa",
            .statePrepared: "Preparato",
            .stateQueued: "In coda",
            .stateRunning: "In esecuzione",
            .stateFinished: "Completato",
            .stateError: "Errore",
            .batchHint: "Il numero parallelo controlla quanti file vengono inseriti in anticipo in ogni lotto di esportazione."
        ],
        .arabic: [
            .appTitle: "تصدير DJIStudio الأصلي",
            .language: "اللغة",
            .osvFiles: "ملفات OSV",
            .dragFilesHere: "اسحب ملفات OSV إلى هنا",
            .orUseAddFiles: "أو استخدم إضافة ملفات",
            .exportSettings: "إعدادات التصدير",
            .preset: "الإعداد المسبق",
            .cleanupTemporaryProjects: "حذف المشاريع المؤقتة بعد التصدير",
            .outputDirectory: "مجلد الإخراج",
            .notSelected: "غير محدد",
            .chooseOutput: "اختر مجلد الإخراج",
            .reveal: "إظهار",
            .clear: "مسح",
            .running: "جارٍ التشغيل...",
            .startExport: "بدء التصدير",
            .stop: "إيقاف",
            .queuedFiles: "الملفات في الانتظار (%@)",
            .runLog: "سجل التشغيل",
            .noOutputYet: "لا يوجد إخراج بعد",
            .lastRun: "آخر تشغيل",
            .lastRunSummary: "الملفات: %@  المشاريع المؤقتة: %@  خطوات التنظيف: %@",
            .errorsSummary: "الأخطاء: %@",
            .ready: "جاهز",
            .noOSVFilesSelected: "لم يتم تحديد ملفات OSV",
            .noOutputDirectorySelected: "لم يتم تحديد مجلد الإخراج",
            .runningExport: "جارٍ التصدير...",
            .exportFinished: "اكتمل التصدير",
            .exportFinishedWithErrors: "اكتمل التصدير مع أخطاء (%@)",
            .failedToLaunchExport: "فشل بدء التصدير: %@",
            .stoppingExport: "جارٍ إيقاف التصدير...",
            .manifest: "البيان: %@",
            .selectedFiles: "يجب أن تنتهي الملفات المحددة بالامتداد .OSV",
            .nativeAppNote: "واجهة Swift أصلية مع خلفية Python مُعتمدة للتصدير.",
            .clickToChooseFiles: "أو انقر على الإطار لاختيار الملفات",
            .frameRate: "معدل الإطارات",
            .sourceFrameRate: "استخدام fps المصدر",
            .bitrate: "معدل البت",
            .low: "منخفض",
            .medium: "متوسط",
            .high: "مرتفع",
            .custom: "مخصص",
            .customBitrateMbps: "معدل بت مخصص (Mbps)",
            .denoise: "إزالة الضوضاء",
            .denoiseMode: "وضع إزالة الضوضاء",
            .performancePriority: "أولوية الأداء",
            .qualityPriority: "أولوية الجودة",
            .tenBit: "10-Bit",
            .parallelCount: "عدد التوازي",
            .progress: "التقدم",
            .statePending: "قيد الانتظار",
            .statePrepared: "تم التحضير",
            .stateQueued: "في قائمة الانتظار",
            .stateRunning: "جارٍ التشغيل",
            .stateFinished: "مكتمل",
            .stateError: "خطأ",
            .batchHint: "عدد التوازي يتحكم في عدد الملفات التي يتم تجهيزها مسبقًا في كل دفعة تصدير."
        ]
    ]

    static func text(_ key: LKey, language: AppLanguage, _ args: [String] = []) -> String {
        let resolved = language == .system ? AppLanguage.resolvedDefault() : language
        let template = translations[resolved]?[key] ?? fallback[key] ?? key.rawValue
        guard !args.isEmpty else { return template }
        var rendered = template
        for value in args {
            guard let range = rendered.range(of: "%@") else { break }
            rendered.replaceSubrange(range, with: value)
        }
        return rendered
    }
}

struct ExportResultSummary: Decodable {
    struct CleanupEntry: Decodable {
        let project_id: Int?
        let live_project_dir: String?
        let removed_dir: Bool?
        let removed_db_row: Bool?
        let clone_dir: String?
        let removed: Bool?
    }

    struct BatchFinalState: Decodable {
        let state: Int
        let outPath: String?
        let synthesisTime: String?
    }

    struct BatchData: Decodable {
        let final_states: [String: BatchFinalState]?
    }

    let files: [String]
    let output_dir: String
    let created_projects: [[String: JSONValue]]
    let errors: [[String: JSONValue]]
    let cleanup: [CleanupEntry]
    let batch: [String: JSONValue]?
    let batch_data: BatchData?
}

struct ExportProgressSnapshot: Decodable {
    struct Summary: Decodable {
        let total: Int
        let completed: Int
        let running: Int
        let queued: Int
    }

    struct Item: Decodable, Identifiable {
        let source: String
        let status: String
        let progress: Double
        let output_path: String?
        let size_bytes: Int?
        let expected_size_bytes: Int?

        var id: String { source }
    }

    let summary: Summary
    let items: [Item]
}

struct DisplayProgressItem {
    let status: String
    let progress: Double
    let sizeBytes: Int
    let expectedSizeBytes: Int

    var clampedProgress: Double {
        max(0.0, min(progress, 1.0))
    }

    var percentageText: String {
        "\(Int((clampedProgress * 100).rounded()))%"
    }
}

enum JSONValue: Decodable, CustomStringConvertible {
    case string(String)
    case number(Double)
    case bool(Bool)
    case array([JSONValue])
    case object([String: JSONValue])
    case null

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() { self = .null }
        else if let value = try? container.decode(Bool.self) { self = .bool(value) }
        else if let value = try? container.decode(Double.self) { self = .number(value) }
        else if let value = try? container.decode(String.self) { self = .string(value) }
        else if let value = try? container.decode([String: JSONValue].self) { self = .object(value) }
        else if let value = try? container.decode([JSONValue].self) { self = .array(value) }
        else { throw DecodingError.dataCorruptedError(in: container, debugDescription: "Unsupported JSON value") }
    }

    var description: String {
        switch self {
        case .string(let value): return value
        case .number(let value): return String(value)
        case .bool(let value): return String(value)
        case .array(let value): return value.map(\.description).joined(separator: ", ")
        case .object(let value): return value.map { "\($0)=\($1)" }.joined(separator: ", ")
        case .null: return "null"
        }
    }
}

@MainActor
final class ExportViewModel: ObservableObject {
    @Published var files: [URL] = []
    @Published var outputDirectory: URL?
    @Published var preset: ExportPreset = .eightK
    @Published var frameRate: FrameRateOption = .source
    @Published var bitrateMode: BitrateModeOption = .high
    @Published var customBitrateMbps = ""
    @Published var enableDenoise = true
    @Published var denoiseMode: DenoiseModeOption = .quality
    @Published var enableTenBit = true
    @Published var parallelCount = 1
    @Published var cleanupTemporaryProjects = true
    @Published var isRunning = false
    @Published var logText = ""
    @Published var statusText = "Ready"
    @Published var lastManifestURL: URL?
    @Published var lastResult: ExportResultSummary?
    @Published var progressSnapshot: ExportProgressSnapshot?
    @Published var language: AppLanguage {
        didSet { UserDefaults.standard.set(language.rawValue, forKey: Self.languageDefaultsKey) }
    }

    private var process: Process?
    private var progressTask: Task<Void, Never>?
    private var autoStopTask: Task<Void, Never>?
    private var stopRequested = false
    private var hasRunUITestScenario = false
    private let projectRoot: URL
    private let runtimeRoot: URL
    private let uiTestScenario: UITestScenario?
    private static let languageDefaultsKey = "native_app_language"

    init() {
        self.projectRoot = ProjectLocator.locateProjectRoot()
        self.runtimeRoot = AppRuntimePaths.ensureRuntimeRoot()
        self.outputDirectory = runtimeRoot.appending(path: "exports", directoryHint: .isDirectory)
        let stored = UserDefaults.standard.string(forKey: Self.languageDefaultsKey)
        self.language = stored.flatMap(AppLanguage.init(rawValue:)) ?? .system
        self.uiTestScenario = UITestScenario.parse(arguments: ProcessInfo.processInfo.arguments)
        self.statusText = localized(.ready)
    }

    func localized(_ key: LKey, _ args: Any...) -> String {
        L10n.text(key, language: language, args.map { String(describing: $0) })
    }

    func localizedStatus(_ status: String) -> String {
        switch status {
        case "pending": return localized(.statePending)
        case "prepared": return localized(.statePrepared)
        case "queued": return localized(.stateQueued)
        case "running": return localized(.stateRunning)
        case "finished": return localized(.stateFinished)
        case "done": return localized(.stateFinished)
        case "error": return localized(.stateError)
        default: return status
        }
    }

    func refreshStatusIfIdle() {
        if !isRunning {
            statusText = localized(.ready)
        }
    }

    func addFiles(_ urls: [URL]) {
        guard !isRunning else { return }
        let normalized = urls
            .filter { $0.pathExtension.lowercased() == "osv" }
            .map { $0.standardizedFileURL }
        for url in normalized where !files.contains(url) {
            files.append(url)
        }
        files.sort { $0.lastPathComponent < $1.lastPathComponent }
    }

    func removeFiles(at offsets: IndexSet) {
        guard !isRunning else { return }
        files.remove(atOffsets: offsets)
    }

    func clearFiles() {
        guard !isRunning else { return }
        files.removeAll()
    }

    func chooseFiles() {
        guard !isRunning else { return }
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = true
        panel.canChooseDirectories = false
        panel.allowedContentTypes = [UTType(filenameExtension: "osv") ?? .data]
        if panel.runModal() == .OK {
            addFiles(panel.urls)
        }
    }

    func chooseOutputDirectory() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.canCreateDirectories = true
        panel.allowsMultipleSelection = false
        if panel.runModal() == .OK, let url = panel.url {
            outputDirectory = url
        }
    }

    func revealOutputDirectory() {
        guard let outputDirectory else { return }
        NSWorkspace.shared.activateFileViewerSelecting([outputDirectory])
    }

    func runUITestScenarioIfNeeded() {
        guard !hasRunUITestScenario else { return }
        hasRunUITestScenario = true
        guard let uiTestScenario else { return }

        if !uiTestScenario.files.isEmpty {
            addFiles(uiTestScenario.files)
        }
        if let outputDirectory = uiTestScenario.outputDirectory {
            self.outputDirectory = outputDirectory
        }
        if let preset = uiTestScenario.preset {
            self.preset = preset
        }
        if let frameRate = uiTestScenario.frameRate {
            self.frameRate = frameRate
        }
        if let bitrateMode = uiTestScenario.bitrateMode {
            self.bitrateMode = bitrateMode
        }
        if let customBitrateMbps = uiTestScenario.customBitrateMbps {
            self.customBitrateMbps = customBitrateMbps
        }
        if let enableDenoise = uiTestScenario.enableDenoise {
            self.enableDenoise = enableDenoise
        }
        if let denoiseMode = uiTestScenario.denoiseMode {
            self.denoiseMode = denoiseMode
        }
        if let enableTenBit = uiTestScenario.enableTenBit {
            self.enableTenBit = enableTenBit
        }
        if let parallelCount = uiTestScenario.parallelCount {
            self.parallelCount = min(max(parallelCount, 1), 8)
        }
        if let cleanupTemporaryProjects = uiTestScenario.cleanupTemporaryProjects {
            self.cleanupTemporaryProjects = cleanupTemporaryProjects
        }

        if uiTestScenario.autostart {
            Task { @MainActor in
                try? await Task.sleep(for: .milliseconds(500))
                self.startExport()
            }
        }
    }

    func startExport() {
        guard !files.isEmpty else {
            statusText = localized(.noOSVFilesSelected)
            return
        }
        guard let outputDirectory else {
            statusText = localized(.noOutputDirectorySelected)
            return
        }
        try? FileManager.default.createDirectory(at: outputDirectory, withIntermediateDirectories: true)

        let runsDirectory = runtimeRoot.appending(path: "runs", directoryHint: .isDirectory)
        try? FileManager.default.createDirectory(at: runsDirectory, withIntermediateDirectories: true)
        let manifestURL = runsDirectory.appending(path: "native_app_export_manifest_\(Int(Date().timeIntervalSince1970)).json")
        let progressURL = runsDirectory.appending(path: "native_app_export_progress_\(Int(Date().timeIntervalSince1970)).json")
        let scriptURL = projectRoot.appending(path: "scripts/dji_studio_export_files.py")

        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        var arguments = [
            "python3",
            scriptURL.path,
            "--output-dir", outputDirectory.path,
            "--resolution-type", preset.resolutionType,
            "--bitrate-mode", bitrateMode.rawValue,
            "--denoise-mode", denoiseMode.rawValue,
            "--parallel-count", String(parallelCount),
            cleanupTemporaryProjects ? "--cleanup-temp-projects" : "--no-cleanup-temp-projects",
            enableDenoise ? "--denoise" : "--no-denoise",
            enableTenBit ? "--ten-bit" : "--no-ten-bit",
            "--progress-manifest", progressURL.path,
            "--manifest", manifestURL.path,
        ]
        arguments.insert(contentsOf: files.map(\.path), at: 2)
        if let frameRateValue = frameRate.frameRateValue {
            arguments.append(contentsOf: ["--frame-rate", frameRateValue])
        }
        if bitrateMode == .custom, let customValue = Double(customBitrateMbps), customValue > 0 {
            arguments.append(contentsOf: ["--custom-bitrate-mbps", String(customValue)])
        }
        process.arguments = arguments
        process.currentDirectoryURL = projectRoot

        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe

        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty, let text = String(data: data, encoding: .utf8) else { return }
            Task { @MainActor in
                self?.logText.append(text)
            }
        }

        process.terminationHandler = { [weak self] proc in
            Task { @MainActor in
                pipe.fileHandleForReading.readabilityHandler = nil
                self?.isRunning = false
                self?.process = nil
                self?.progressTask?.cancel()
                self?.progressTask = nil
                self?.autoStopTask?.cancel()
                self?.autoStopTask = nil
                self?.lastManifestURL = manifestURL
                if self?.stopRequested == true {
                    self?.statusText = self?.localized(.exportStopped) ?? ""
                } else {
                    self?.statusText = proc.terminationStatus == 0
                        ? (self?.localized(.exportFinished) ?? "")
                        : (self?.localized(.exportFinishedWithErrors, proc.terminationStatus) ?? "")
                }
                if let data = try? Data(contentsOf: manifestURL),
                   let summary = try? JSONDecoder().decode(ExportResultSummary.self, from: data) {
                    self?.lastResult = summary
                }
                self?.stopRequested = false
            }
        }

        do {
            logText = ""
            lastResult = nil
            lastManifestURL = nil
            progressSnapshot = nil
            autoStopTask?.cancel()
            autoStopTask = nil
            stopRequested = false
            statusText = localized(.runningExport)
            isRunning = true
            self.process = process
            try process.run()
            startProgressPolling(progressURL)
            if let seconds = uiTestScenario?.autostopAfter, seconds > 0 {
                autoStopTask = Task { [weak self] in
                    try? await Task.sleep(for: .seconds(seconds))
                    await MainActor.run {
                        guard let self, self.isRunning else { return }
                        self.stopExport()
                    }
                }
            }
        } catch {
            statusText = localized(.failedToLaunchExport, error.localizedDescription)
            isRunning = false
            self.process = nil
        }
    }

    func stopExport() {
        stopRequested = true
        process?.terminate()
        progressTask?.cancel()
        progressTask = nil
        autoStopTask?.cancel()
        autoStopTask = nil
        statusText = localized(.stoppingExport)
    }

    private func startProgressPolling(_ progressURL: URL) {
        progressTask?.cancel()
        progressTask = Task { [weak self] in
            while !Task.isCancelled {
                if let data = try? Data(contentsOf: progressURL),
                   let snapshot = try? JSONDecoder().decode(ExportProgressSnapshot.self, from: data) {
                    await MainActor.run {
                        self?.progressSnapshot = snapshot
                    }
                }
                try? await Task.sleep(for: .seconds(1))
            }
        }
    }

    func displayProgress(for file: URL) -> DisplayProgressItem {
        if let item = progressSnapshot?.items.first(where: { $0.source == file.path }) {
            return DisplayProgressItem(
                status: item.status,
                progress: item.progress,
                sizeBytes: item.size_bytes ?? 0,
                expectedSizeBytes: item.expected_size_bytes ?? 0
            )
        }
        if isRunning {
            return DisplayProgressItem(status: "queued", progress: 0.0, sizeBytes: 0, expectedSizeBytes: 0)
        }
        return DisplayProgressItem(status: "pending", progress: 0.0, sizeBytes: 0, expectedSizeBytes: 0)
    }
}

enum AppRuntimePaths {
    static func ensureRuntimeRoot() -> URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSHomeDirectory()).appending(path: "Library/Application Support", directoryHint: .isDirectory)
        let root = base.appending(path: "DJIStudioNativeApp", directoryHint: .isDirectory)
        try? FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        try? FileManager.default.createDirectory(at: root.appending(path: "exports", directoryHint: .isDirectory), withIntermediateDirectories: true)
        try? FileManager.default.createDirectory(at: root.appending(path: "runs", directoryHint: .isDirectory), withIntermediateDirectories: true)
        return root
    }
}

enum ProjectLocator {
    static func locateProjectRoot() -> URL {
        let env = ProcessInfo.processInfo.environment["DJI_STUDIO_PROJECT_ROOT"].map(URL.init(fileURLWithPath:))
        let cwd = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
        let compiledRoot = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
        let fallback = URL(fileURLWithPath: "/Users/gordonyoung/Desktop/Projects/DJIStudio")

        for candidate in [env, cwd, compiledRoot, fallback].compactMap({ $0 }) {
            let script = candidate.appending(path: "scripts/dji_studio_export_files.py")
            if FileManager.default.fileExists(atPath: script.path) {
                return candidate
            }
        }
        return fallback
    }
}

struct UITestScenario {
    let files: [URL]
    let outputDirectory: URL?
    let preset: ExportPreset?
    let frameRate: FrameRateOption?
    let bitrateMode: BitrateModeOption?
    let customBitrateMbps: String?
    let enableDenoise: Bool?
    let denoiseMode: DenoiseModeOption?
    let enableTenBit: Bool?
    let parallelCount: Int?
    let cleanupTemporaryProjects: Bool?
    let autostart: Bool
    let autostopAfter: TimeInterval?

    static func parse(arguments: [String]) -> UITestScenario? {
        func value(for flag: String) -> String? {
            guard let idx = arguments.firstIndex(of: flag), idx + 1 < arguments.count else { return nil }
            return arguments[idx + 1]
        }

        func values(for flag: String) -> [String] {
            arguments.enumerated()
                .filter { $0.element == flag && $0.offset + 1 < arguments.count }
                .map { arguments[$0.offset + 1] }
        }

        func has(_ flag: String) -> Bool { arguments.contains(flag) }

        let files = values(for: "--ui-test-file")
            .map { URL(fileURLWithPath: $0).standardizedFileURL }
            .filter { FileManager.default.fileExists(atPath: $0.path) }

        if files.isEmpty, !has("--ui-test-autostart"), !has("--ui-test-autostop-after") {
            return nil
        }

        let outputDirectory = value(for: "--ui-test-output-dir").map {
            URL(fileURLWithPath: $0, isDirectory: true).standardizedFileURL
        }
        let preset = value(for: "--ui-test-preset").flatMap {
            switch $0.lowercased() {
            case "6k": return ExportPreset.sixK
            case "8k": return ExportPreset.eightK
            default: return nil
            }
        }
        let frameRate = value(for: "--ui-test-frame-rate").flatMap {
            switch $0 {
            case "source": return FrameRateOption.source
            case "24": return .fps24
            case "25": return .fps25
            case "30": return .fps30
            case "50": return .fps50
            case "60": return .fps60
            default: return nil
            }
        }
        let bitrateMode = value(for: "--ui-test-bitrate-mode").flatMap(BitrateModeOption.init(rawValue:))
        let customBitrateMbps = value(for: "--ui-test-custom-bitrate")
        let enableDenoise: Bool? = has("--ui-test-denoise") ? true : (has("--ui-test-no-denoise") ? false : nil)
        let denoiseMode = value(for: "--ui-test-denoise-mode").flatMap(DenoiseModeOption.init(rawValue:))
        let enableTenBit: Bool? = has("--ui-test-ten-bit") ? true : (has("--ui-test-no-ten-bit") ? false : nil)
        let parallelCount = value(for: "--ui-test-parallel-count").flatMap(Int.init)
        let cleanupTemporaryProjects: Bool? = has("--ui-test-cleanup-temp-projects") ? true : (has("--ui-test-no-cleanup-temp-projects") ? false : nil)
        let autostart = has("--ui-test-autostart")
        let autostopAfter = value(for: "--ui-test-autostop-after").flatMap(Double.init)

        return UITestScenario(
            files: files,
            outputDirectory: outputDirectory,
            preset: preset,
            frameRate: frameRate,
            bitrateMode: bitrateMode,
            customBitrateMbps: customBitrateMbps,
            enableDenoise: enableDenoise,
            denoiseMode: denoiseMode,
            enableTenBit: enableTenBit,
            parallelCount: parallelCount,
            cleanupTemporaryProjects: cleanupTemporaryProjects,
            autostart: autostart,
            autostopAfter: autostopAfter
        )
    }
}

struct ContentView: View {
    @ObservedObject var viewModel: ExportViewModel

    var body: some View {
        VStack(spacing: 16) {
            header
            VSplitView {
                HSplitView {
                    dropPane
                        .frame(minWidth: 420, idealWidth: 640, maxWidth: .infinity, minHeight: 280)
                    controlsPane
                        .frame(minWidth: 320, idealWidth: 360, maxWidth: 400, minHeight: 280)
                }
                .frame(minHeight: 300, idealHeight: 340, maxHeight: 420)

                HSplitView {
                    fileList
                        .frame(minWidth: 420, idealWidth: 620, maxWidth: .infinity, minHeight: 260)
                    logPane
                        .frame(minWidth: 320, idealWidth: 420, maxWidth: .infinity, minHeight: 260)
                }
                .frame(minHeight: 260)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

            footer
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .padding(16)
        .onChange(of: viewModel.language) { _, _ in
            viewModel.refreshStatusIfIdle()
        }
        .task {
            viewModel.runUITestScenarioIfNeeded()
        }
    }

    private var header: some View {
        HStack(alignment: .center) {
            VStack(alignment: .leading, spacing: 4) {
                Text(viewModel.localized(.appTitle))
                    .font(.title2.weight(.semibold))
                Text(viewModel.localized(.nativeAppNote))
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            VStack(alignment: .leading, spacing: 6) {
                Text(viewModel.localized(.language))
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Picker(viewModel.localized(.language), selection: $viewModel.language) {
                    ForEach(AppLanguage.allCases) { language in
                        Text(language.displayName).tag(language)
                    }
                }
                .labelsHidden()
                .frame(width: 220)
            }
        }
    }

    private var dropPane: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(viewModel.localized(.osvFiles))
                .font(.headline)
            ZStack {
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color(nsColor: .controlBackgroundColor))
                RoundedRectangle(cornerRadius: 16)
                    .strokeBorder(style: StrokeStyle(lineWidth: 2, dash: [8]))
                    .foregroundStyle(.secondary)
                VStack(spacing: 8) {
                    Image(systemName: "tray.and.arrow.down")
                        .font(.system(size: 28))
                    Text(viewModel.localized(.dragFilesHere))
                    Text(viewModel.localized(.clickToChooseFiles))
                        .foregroundStyle(.secondary)
                        .font(.caption)
                }
            }
            .frame(minHeight: 180)
            .contentShape(Rectangle())
            .onTapGesture { viewModel.chooseFiles() }
            .dropDestination(for: URL.self) { items, _ in
                guard !viewModel.isRunning else { return false }
                viewModel.addFiles(items)
                return true
            }
        }
    }

    private var controlsPane: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                Text(viewModel.localized(.exportSettings))
                    .font(.headline)
                Picker(viewModel.localized(.preset), selection: $viewModel.preset) {
                    ForEach(ExportPreset.allCases) { preset in
                        Text(preset.rawValue).tag(preset)
                    }
                }
                .pickerStyle(.segmented)

                VStack(alignment: .leading, spacing: 6) {
                    Text(viewModel.localized(.frameRate))
                        .font(.subheadline)
                    Picker(viewModel.localized(.frameRate), selection: $viewModel.frameRate) {
                        Text(viewModel.localized(.sourceFrameRate)).tag(FrameRateOption.source)
                        Text("24 fps").tag(FrameRateOption.fps24)
                        Text("25 fps").tag(FrameRateOption.fps25)
                        Text("30 fps").tag(FrameRateOption.fps30)
                        Text("50 fps").tag(FrameRateOption.fps50)
                        Text("60 fps").tag(FrameRateOption.fps60)
                    }
                }

                VStack(alignment: .leading, spacing: 6) {
                    Text(viewModel.localized(.bitrate))
                        .font(.subheadline)
                    Picker(viewModel.localized(.bitrate), selection: $viewModel.bitrateMode) {
                        Text(viewModel.localized(.low)).tag(BitrateModeOption.low)
                        Text(viewModel.localized(.medium)).tag(BitrateModeOption.medium)
                        Text(viewModel.localized(.high)).tag(BitrateModeOption.high)
                        Text(viewModel.localized(.custom)).tag(BitrateModeOption.custom)
                    }
                    .pickerStyle(.segmented)
                    if viewModel.bitrateMode == .custom {
                        TextField(viewModel.localized(.customBitrateMbps), text: $viewModel.customBitrateMbps)
                            .textFieldStyle(.roundedBorder)
                    }
                }

                Toggle(viewModel.localized(.denoise), isOn: $viewModel.enableDenoise)
                if viewModel.enableDenoise {
                    Picker(viewModel.localized(.denoiseMode), selection: $viewModel.denoiseMode) {
                        Text(viewModel.localized(.performancePriority)).tag(DenoiseModeOption.performance)
                        Text(viewModel.localized(.qualityPriority)).tag(DenoiseModeOption.quality)
                    }
                    .pickerStyle(.segmented)
                }

                Toggle(viewModel.localized(.tenBit), isOn: $viewModel.enableTenBit)

                Stepper(value: $viewModel.parallelCount, in: 1...8) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(viewModel.localized(.parallelCount)): \(viewModel.parallelCount)")
                        Text(viewModel.localized(.batchHint))
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                }

                Toggle(viewModel.localized(.cleanupTemporaryProjects), isOn: $viewModel.cleanupTemporaryProjects)

                VStack(alignment: .leading, spacing: 6) {
                    Text(viewModel.localized(.outputDirectory))
                        .font(.subheadline)
                    Text(viewModel.outputDirectory?.path ?? viewModel.localized(.notSelected))
                        .font(.system(size: 11, weight: .regular, design: .monospaced))
                        .foregroundStyle(.secondary)
                        .textSelection(.enabled)
                    HStack {
                        Button(viewModel.localized(.chooseOutput)) { viewModel.chooseOutputDirectory() }
                        Button(viewModel.localized(.reveal)) { viewModel.revealOutputDirectory() }
                            .disabled(viewModel.outputDirectory == nil)
                    }
                }
                Button(viewModel.localized(.clear)) { viewModel.clearFiles() }
                    .disabled(viewModel.files.isEmpty || viewModel.isRunning)

                Divider()

                HStack {
                    Button(viewModel.isRunning ? viewModel.localized(.running) : viewModel.localized(.startExport)) {
                        viewModel.startExport()
                    }
                    .disabled(viewModel.isRunning || viewModel.files.isEmpty)

                    Button(viewModel.localized(.stop)) { viewModel.stopExport() }
                        .disabled(!viewModel.isRunning)
                }

                Text(viewModel.statusText)
                    .font(.footnote)
                    .foregroundStyle(.secondary)

                if let manifest = viewModel.lastManifestURL {
                    Text(viewModel.localized(.manifest, manifest.path))
                        .font(.system(size: 11, weight: .regular, design: .monospaced))
                        .foregroundStyle(.secondary)
                        .textSelection(.enabled)
                }
            }
            .frame(maxWidth: .infinity, alignment: .topLeading)
        }
        .frame(width: 340, alignment: .topLeading)
    }

    private var fileList: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(viewModel.localized(.queuedFiles, viewModel.files.count.formatted()))
                .font(.headline)
            List {
                ForEach(viewModel.files, id: \.path) { file in
                    let progressItem = viewModel.displayProgress(for: file)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(file.lastPathComponent)
                        Text(file.path)
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundStyle(.secondary)
                            .lineLimit(2)
                        HStack {
                            Text(viewModel.localizedStatus(progressItem.status))
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            Spacer()
                            Text(progressItem.percentageText)
                                .font(.caption.monospacedDigit())
                                .foregroundStyle(.secondary)
                        }
                        ProgressView(value: progressItem.clampedProgress)
                        HStack(spacing: 8) {
                            Text(ByteCountFormatter.string(fromByteCount: Int64(progressItem.sizeBytes), countStyle: .file))
                                .font(.caption2)
                                .foregroundStyle(.secondary)
                            if progressItem.expectedSizeBytes > 0 {
                                Text("/ \(ByteCountFormatter.string(fromByteCount: Int64(progressItem.expectedSizeBytes), countStyle: .file))")
                                    .font(.caption2)
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }
                }
                .onDelete(perform: viewModel.removeFiles)
            }
            .deleteDisabled(viewModel.isRunning)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }

    private var logPane: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(viewModel.localized(.runLog))
                .font(.headline)
            ScrollView {
                Text(viewModel.logText.isEmpty ? viewModel.localized(.noOutputYet) : viewModel.logText)
                    .frame(maxWidth: .infinity, alignment: .topLeading)
                    .font(.system(size: 11, design: .monospaced))
                    .textSelection(.enabled)
                    .padding(10)
            }
            .background(Color(nsColor: .textBackgroundColor))
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }

    private var footer: some View {
        VStack(alignment: .leading, spacing: 6) {
            if let result = viewModel.lastResult {
                Text(viewModel.localized(.lastRun))
                    .font(.headline)
                Text(viewModel.localized(.lastRunSummary, String(result.files.count), String(result.created_projects.count), String(result.cleanup.count)))
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                if !result.errors.isEmpty {
                    let errorText = result.errors
                        .map { $0.map { "\($0.key)=\($0.value)" }.joined(separator: ", ") }
                        .joined(separator: " | ")
                    Text(viewModel.localized(.errorsSummary, errorText))
                        .font(.footnote)
                        .foregroundStyle(.red)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .fixedSize(horizontal: false, vertical: true)
    }
}
