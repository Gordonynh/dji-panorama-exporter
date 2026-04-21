// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "DJIStudioNativeApp",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "DJIStudioNativeApp", targets: ["DJIStudioNativeApp"])
    ],
    targets: [
        .executableTarget(
            name: "DJIStudioNativeApp"
        )
    ]
)
