import SwiftUI

@main
struct ZenBarApp: App {
    @StateObject private var statusManager = StatusBarManager()

    var body: some Scene {
        Settings {
            EmptyView()
        }
    }
}
