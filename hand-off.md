# Project Hand-off
**Current Version:** v1.0.5

## Recent Changes (v1.0.5)
- Automatically terminate older/duplicate `DirectTrans` instances on launch.
- Concurrency and reliability fixes: threading locks for hotkeys, destroyed window state checks, keyboard hook lifecycle cleanup.
- Clipboard and UI fixes: preserve clipboard content during settings key save, restore active window focus before pasting, fix tab characters in RTF.
- Expanded Windows font support: retrieve per-user custom fonts from user registry hives.
- Simplified API testing workflow and reduced polling footprint to conserve system resources.

## Next Steps
- Verify the build executable `DirectTrans_v1.0.5.exe` functions correctly.
- Test keyboard shortcut responsiveness and the multi-instance termination logic.
- Run tests again after deployment to make sure no platform-specific issues occur.
