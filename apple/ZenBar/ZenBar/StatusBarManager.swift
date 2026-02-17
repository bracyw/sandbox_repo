import AppKit
import SwiftUI

final class StatusBarManager: NSObject, ObservableObject {
    private var drawerItem: NSStatusItem?
    private let popover = NSPopover()

    private var toggleItem: NSStatusItem?

    private var curtainWindow: NSWindow?
    private var isCurtainVisible = true

    override init() {
        super.init()

        setupCurtainWindow()

        toggleItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = toggleItem?.button {
            button.image = NSImage(systemSymbolName: "chevron.right", accessibilityDescription: "Toggle hider")
            button.action = #selector(toggleCurtain)
            button.target = self
        }

        drawerItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = drawerItem?.button {
            button.image = NSImage(systemSymbolName: "ellipsis", accessibilityDescription: "More")
            button.action = #selector(togglePopover)
            button.target = self
        }

        popover.contentViewController = NSHostingController(rootView: DrawerContentView())
        popover.behavior = .transient
    }

    private func setupCurtainWindow() {
        guard let screen = NSScreen.main else { return }

        let menuBarHeight = screen.frame.height - screen.visibleFrame.height - max(screen.visibleFrame.origin.y, 0)
        let curtainWidth: CGFloat = 300

        let curtainRect = NSRect(
            x: screen.frame.midX + 80,
            y: screen.frame.height - menuBarHeight,
            width: curtainWidth,
            height: menuBarHeight
        )

        let window = NSWindow(
            contentRect: curtainRect,
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )

        window.level = .statusBar + 1
        window.backgroundColor = .clear
        window.isOpaque = false
        window.hasShadow = false

        let visualEffect = NSVisualEffectView(frame: NSRect(origin: .zero, size: curtainRect.size))
        visualEffect.material = .menu
        visualEffect.blendingMode = .withinWindow
        visualEffect.state = .active

        window.contentView = visualEffect
        window.orderFront(nil)

        curtainWindow = window
    }

    @objc private func toggleCurtain() {
        if isCurtainVisible {
            curtainWindow?.orderOut(nil)
            toggleItem?.button?.image = NSImage(systemSymbolName: "chevron.left", accessibilityDescription: "Show")
        } else {
            curtainWindow?.orderFront(nil)
            toggleItem?.button?.image = NSImage(systemSymbolName: "chevron.right", accessibilityDescription: "Hide")
        }

        isCurtainVisible.toggle()
    }

    @objc private func togglePopover(_ sender: AnyObject?) {
        guard let button = drawerItem?.button else { return }

        if popover.isShown {
            popover.performClose(sender)
        } else {
            popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
        }
    }
}

struct DrawerContentView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Hidden Items")
                .font(.headline)
                .padding(.bottom, 5)

            HStack {
                LaunchButton(name: "Terminal", icon: "terminal.fill")
                LaunchButton(name: "Activity", icon: "waveform.path.ecg")
                LaunchButton(name: "Music", icon: "music.note")
            }

            Divider()

            Button("Quit ZenBar") {
                NSApplication.shared.terminate(nil)
            }
            .buttonStyle(.plain)
            .foregroundStyle(.secondary)
        }
        .padding()
        .frame(width: 220)
    }
}

struct LaunchButton: View {
    let name: String
    let icon: String

    var body: some View {
        Button {
            print("Launching \(name)")
        } label: {
            VStack {
                Image(systemName: icon)
                    .font(.system(size: 20))
                Text(name)
                    .font(.caption)
            }
            .frame(width: 56, height: 56)
            .background(Color.black.opacity(0.1))
            .cornerRadius(8)
        }
        .buttonStyle(.plain)
    }
}
