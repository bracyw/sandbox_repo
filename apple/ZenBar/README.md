# ZenBar (macOS SwiftUI)

ZenBar is a native macOS menu bar utility prototype that implements a sustainable "Curtain & Drawer" architecture:

- **Curtain**: a blur shield window layered over part of the menu bar to visually hide right-side status icons.
- **Drawer**: a `...` status item that opens a popover with quick-launch placeholders.

## Open and run

1. Open `apple/ZenBar/ZenBar.xcodeproj` in Xcode.
2. Select the `ZenBar` scheme.
3. Run with <kbd>⌘R</kbd>.

## Behavior

- The app runs as an **agent app** (`LSUIElement = YES`) so it does not appear in the Dock.
- Two menu bar items are created:
  - `>` toggles the blur curtain on/off.
  - `...` opens the drawer popover.

## M4 notch tuning

The curtain placement can be tuned in `StatusBarManager.setupCurtainWindow()` by changing:

- `x: screen.frame.midX + 80`
- `curtainWidth: 300`

These values are intentionally explicit so you can quickly tune for different notch/icon layouts.
