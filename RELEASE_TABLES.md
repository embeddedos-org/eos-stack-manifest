# EoS Stack — Release Tables

> Source: [embeddedos-org](https://github.com/embeddedos-org) | Manifest: [eos-stack-manifest](https://github.com/embeddedos-org/eos-stack-manifest)
>
> **Legend:** ✅ Available & released | 🔨 In progress / partial | 🚧 Scaffolded, not yet buildable | ❌ Not started | ⚠️ Blocked (see Barriers column)

---

## 1. Test Coverage Table

All Python repos target **100% line coverage** (`fail_under = 100` in `.coveragerc`). Web repos use Vitest with V8 provider. Go uses `go test -coverprofile`. Firmware uses gcov/lcov.

| Repo | Platform | Test Framework | Coverage Tool | Line Target | Branch Coverage | CI Status |
|------|----------|---------------|---------------|-------------|-----------------|-----------|
| [eos](https://github.com/embeddedos-org/eos) | Firmware | Unity / CTest | gcov + lcov | 100% | Yes | ✅ |
| [eBoot](https://github.com/embeddedos-org/eBoot) | Firmware | Unity / CTest | gcov + lcov | 100% | Yes | ✅ |
| [eAI](https://github.com/embeddedos-org/eAI) | Firmware | Unity / CTest | gcov + lcov | 100% | Yes | ✅ |
| [eosllm](https://github.com/embeddedos-org/eosllm) | Firmware | Makefile test target | gcov | 100% | Yes | ✅ |
| [eNI](https://github.com/embeddedos-org/eNI) | Firmware | Unity / CTest | gcov + lcov | 100% | Yes | ✅ |
| [ebuild](https://github.com/embeddedos-org/ebuild) | Firmware/Host | CTest | gcov | 100% | Yes | ✅ |
| [HEALTH-BAND-Neuro](https://github.com/embeddedos-org/HEALTH-BAND-Neuro) | Firmware | Zephyr test suite | gcov | 100% | Yes | ✅ |
| [eVera](https://github.com/embeddedos-org/eVera) | Desktop/AI | pytest | coverage.py | **100%** | Yes | ✅ |
| [EoStudio](https://github.com/embeddedos-org/EoStudio) | Desktop | pytest | coverage.py | **100%** | Yes | ✅ |
| [EoSim](https://github.com/embeddedos-org/EoSim) | Desktop | pytest | coverage.py | **100%** | Yes | ✅ |
| [eDB](https://github.com/embeddedos-org/eDB) | Desktop/Web | pytest + Vitest | coverage.py + V8 | 100% / 30% | Yes | ✅ |
| [eIPC](https://github.com/embeddedos-org/eIPC) | Desktop | go test | go cover | 100% | Yes | ✅ |
| [eBrowser](https://github.com/embeddedos-org/eBrowser) | Desktop | pytest + CTest | coverage.py + gcov | 100% | Yes | ✅ |
| [eOffice](https://github.com/embeddedos-org/eOffice) | Desktop/Web | pytest + Vitest | coverage.py + V8 | 100% | Yes | ✅ |
| [HealthKey-Ulta](https://github.com/embeddedos-org/HealthKey-Ulta) | Mobile/Web | pytest | coverage.py | 100% | Yes | ✅ |
| [eApps](https://github.com/embeddedos-org/eApps) | Web | pytest | coverage.py | 100% | Yes | ✅ |
| [www.embeddedos.org](https://github.com/embeddedos-org/www.embeddedos.org) | Web | Vitest | V8 | 100% | Yes | ✅ |
| [eCAD-Hardware-Products](https://github.com/embeddedos-org/eCAD-Hardware-Products) | Hardware | N/A (CAD/HTML) | N/A | N/A | N/A | ✅ |

---

## 2. Release Binaries Table

### 2a. Firmware Binaries

| Binary File | Repo | Format | Target MCU / SoC | Architecture | Toolchain | Available |
|-------------|------|--------|-----------------|--------------|-----------|-----------|
| `eos.elf` | eos | ELF | ARM Cortex-M4/M7, RISC-V | ARMv7-M, RV32 | arm-none-eabi-gcc 13 | ✅ |
| `eos.hex` | eos | Intel HEX | ARM Cortex-M4/M7 | ARMv7-M | arm-none-eabi-gcc 13 | ✅ |
| `eos.bin` | eos | Raw binary | ARM Cortex-M4/M7 | ARMv7-M | arm-none-eabi-gcc 13 | ✅ |
| `eBoot.elf` | eBoot | ELF | Any ARM Cortex-M | ARMv7-M | arm-none-eabi-gcc 13 | ✅ |
| `eBoot.hex` | eBoot | Intel HEX | Any ARM Cortex-M | ARMv7-M | arm-none-eabi-gcc 13 | ✅ |
| `eAI.elf` | eAI | ELF | Cortex-M55, Cortex-A55 | ARMv8.1-M, ARMv8-A | arm-none-eabi-gcc 13 | ✅ |
| `libeosllm.a` | eosllm | Static library | ARM Cortex-M7+ | ARMv7E-M | arm-none-eabi-gcc 13 | ✅ |
| `eNI.elf` | eNI | ELF | ARM Cortex-M4 | ARMv7-M | arm-none-eabi-gcc 13 | ✅ |
| `ebuild` (host) | ebuild | Native binary | x86_64 / ARM64 host | x86_64, ARM64 | GCC/Clang | ✅ |
| `health_band_neuro.elf` | HEALTH-BAND-Neuro | ELF | Nordic nRF52840 | ARM Cortex-M4F | arm-none-eabi-gcc 13 | ✅ |
| `health_band_neuro.hex` | HEALTH-BAND-Neuro | Intel HEX | Nordic nRF52840 | ARM Cortex-M4F | arm-none-eabi-gcc 13 | ✅ |

### 2b. Desktop Binaries (Linux / macOS / Windows)

| Binary File | Repo | Platform | Architecture | Build System | Available | Barriers |
|-------------|------|----------|--------------|-------------|-----------|----------|
| `eipc-linux-amd64` | eIPC | Linux | x86_64 | `go build` | ✅ | None |
| `eipc-linux-arm64` | eIPC | Linux | ARM64 | `go build` | ✅ | None |
| `eipc-windows-amd64.exe` | eIPC | Windows | x86_64 | `GOOS=windows go build` | ✅ | None |
| `eipc-darwin-amd64` | eIPC | macOS | x86_64 | `GOOS=darwin go build` | ✅ | None |
| `eipc-darwin-arm64` | eIPC | macOS | Apple Silicon | `GOOS=darwin GOARCH=arm64` | ✅ | None |
| `eVera-linux.AppImage` | eVera | Linux | x86_64 | PyInstaller | ✅ | None |
| `eVera-windows.exe` | eVera | Windows | x86_64 | PyInstaller | 🔨 | Requires Windows runner in CI; cross-compile not supported by PyInstaller |
| `eVera-macos.dmg` | eVera | macOS | x86_64 / ARM64 | PyInstaller | 🔨 | Requires macOS runner; Apple notarization needed for distribution |
| `EoStudio-linux.AppImage` | EoStudio | Linux | x86_64 | PyInstaller | ✅ | None |
| `EoStudio-windows.exe` | EoStudio | Windows | x86_64 | PyInstaller | 🔨 | Requires Windows runner in CI |
| `EoStudio-macos.dmg` | EoStudio | macOS | x86_64 / ARM64 | PyInstaller | 🔨 | Requires macOS runner; Apple notarization |
| `EoSim-linux.AppImage` | EoSim | Linux | x86_64 | PyInstaller | ✅ | None |
| `EoSim-windows.exe` | EoSim | Windows | x86_64 | PyInstaller | 🔨 | Requires Windows runner in CI |
| `EoSim-macos.dmg` | EoSim | macOS | x86_64 / ARM64 | PyInstaller | 🔨 | Requires macOS runner |
| `eDB-linux.AppImage` | eDB | Linux | x86_64 | Electron Builder | 🔨 | Electron packaging not yet wired in CI |
| `eDB-windows.exe` | eDB | Windows | x86_64 | Electron Builder | 🔨 | Requires Windows runner; code signing cert |
| `eDB-macos.dmg` | eDB | macOS | x86_64 / ARM64 | Electron Builder | 🔨 | Requires macOS runner; Apple notarization |
| `eBrowser-linux` | eBrowser | Linux | x86_64 | CMake + Ninja | ✅ | None |
| `eBrowser-windows.exe` | eBrowser | Windows | x86_64 | CMake + MSVC | 🔨 | Requires Windows runner; MSVC toolchain |
| `eBrowser-macos` | eBrowser | macOS | x86_64 / ARM64 | CMake + Clang | 🔨 | Requires macOS runner |
| `eOffice-linux.AppImage` | eOffice | Linux | x86_64 | Electron Builder | 🔨 | Electron packaging not yet wired in CI |
| `eOffice-windows.exe` | eOffice | Windows | x86_64 | Electron Builder | 🔨 | Requires Windows runner; code signing cert |
| `eOffice-macos.dmg` | eOffice | macOS | x86_64 / ARM64 | Electron Builder | 🔨 | Requires macOS runner; Apple notarization |

### 2c. Mobile Binaries (iOS / Android)

| Binary / Package | Repo | Platform | Framework | Build System | Available | Barriers |
|-----------------|------|----------|-----------|-------------|-----------|----------|
| `HealthKey-Ulta.apk` | HealthKey-Ulta | Android | React Native / Expo | `eas build --platform android` | 🚧 | `mobile-app/` directory has only `.gitignore`; React Native scaffold not yet committed |
| `HealthKey-Ulta.aab` | HealthKey-Ulta | Android (Play Store) | React Native / Expo | `eas build --platform android --profile production` | 🚧 | Same as above; Google Play signing key required |
| `HealthKey-Ulta.ipa` | HealthKey-Ulta | iOS | React Native / Expo | `eas build --platform ios` | ⚠️ | Requires Apple Developer account ($99/yr), provisioning profile, and macOS runner |
| `eVera-android.apk` | eVera | Android | React Native (mobile/) | `eas build` | 🔨 | `mobile/` scaffold present; Expo config exists; EAS project ID not set |
| `eVera-ios.ipa` | eVera | iOS | React Native (mobile/) | `eas build --platform ios` | ⚠️ | Apple Developer account required; provisioning profile missing |
| `EoSim-android.apk` | EoSim | Android | Capacitor (android/) | `./gradlew assembleRelease` | 🔨 | `android/app/` scaffold present; Capacitor sync not run in CI |
| `EoSim-ios.ipa` | EoSim | iOS | Capacitor (ios/) | Xcode build | ⚠️ | `ios/EoSim/` scaffold present; requires macOS runner + Apple Developer account |
| `eBrowser-android.apk` | eBrowser | Android | Expo (mobile/) | `eas build --platform android` | 🔨 | `mobile/` has Expo config; EAS project ID not set; BLE permissions needed |
| `eBrowser-ios.ipa` | eBrowser | iOS | Expo (mobile/) | `eas build --platform ios` | ⚠️ | Requires Apple Developer account; BLE entitlements |

### 2d. Browser Extensions

| Extension Package | Repo | Browser Targets | Manifest Version | Build System | Available | Barriers |
|------------------|------|----------------|-----------------|-------------|-----------|----------|
| `eVera-extension.zip` | eVera | Chrome, Edge, Brave, Opera | MV3 | `zip extension/` | ✅ | None — extension/ has full MV3 manifest, background.js, content.js |
| `eVera-vscode.vsix` | eVera | VS Code | N/A | `vsce package` | 🔨 | `vscode-extension/` scaffold present; `vsce` not yet run in CI |
| `eBrowser-extension.zip` | eBrowser | Chrome, Edge, Brave, Firefox | MV3 | `zip extension/` | ✅ | None — full MV3 manifest with newtab, options, popup |
| `eOffice-browser-extension.zip` | eOffice | Chrome, Edge, Brave | MV3 | `zip extensions/browser/` | 🔨 | `extensions/browser/` present; packaging step not yet in CI |
| `eOffice-github-extension.zip` | eOffice | GitHub (browser) | MV3 | `zip extensions/github/` | 🔨 | Scaffold present; not yet packaged |
| `eOffice-google-workspace.zip` | eOffice | Google Workspace | Add-on | `zip extensions/google-workspace/` | 🔨 | Scaffold present; Google Workspace OAuth needed |
| `eOffice-office365.zip` | eOffice | Microsoft Office 365 | Office Add-in | `zip extensions/office365/` | 🔨 | Scaffold present; Microsoft 365 manifest + signing needed |
| `eOffice-jetbrains.zip` | eOffice | JetBrains IDEs | Plugin | `zip extensions/jetbrains/` | 🔨 | Scaffold present; Gradle build not yet in CI |
| `eOffice-obsidian.zip` | eOffice | Obsidian | Plugin | `zip extensions/obsidian/` | 🔨 | Scaffold present; not yet packaged |
| `HealthKey-extension.zip` | HealthKey-Ulta | Chrome, Edge, Brave | MV3 | `zip browser-extension/healthkey/` | ✅ | None — full MV3 manifest, background.js, content.js, popup |

### 2e. Web / PWA Packages

| Package | Repo | Type | Build Command | Available | Barriers |
|---------|------|------|--------------|-----------|----------|
| `eApps-web.zip` | eApps | Static Web | `npm run build` | ✅ | None |
| `eOffice-web.zip` | eOffice | Web App | `npm run build` | ✅ | None |
| `www.embeddedos.org-web.zip` | www.embeddedos.org | Marketing Site | `npm run build` | ✅ | None |
| `HealthKey-web.zip` | HealthKey-Ulta | PWA Dashboard | Static HTML | ✅ | None — `web-app/healthkey-dashboard/` has index.html + sw.js |
| `eDB-web.zip` | eDB | Web App | `npm run build` | ✅ | None |
| `eBrowser-web.zip` | eBrowser | Web App | Static | 🔨 | `web-app/` present; build step not yet in CI |
| `eOffice-browser-apps.zip` | eOffice | Browser-based apps | Static HTML | ✅ | `browser/` has full set of HTML apps |
| `embeddedos-org.github.io.zip` | embeddedos-org.github.io | GitHub Pages | Static HTML | ✅ | None |

---

## 3. Platform Compatibility Matrix

### 3a. Application Platform Support

| Application | Linux | macOS | Windows | Android | iOS | Chrome Ext | Firefox Ext | VS Code Ext | PWA / Web |
|-------------|:-----:|:-----:|:-------:|:-------:|:---:|:----------:|:-----------:|:-----------:|:---------:|
| **eVera** (AI Agent) | ✅ | 🔨 | 🔨 | 🔨 | ⚠️ | ✅ | ❌ | 🔨 | ✅ |
| **EoStudio** (IDE) | ✅ | 🔨 | 🔨 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **EoSim** (Simulator) | ✅ | 🔨 | 🔨 | 🔨 | ⚠️ | 🔨 | ❌ | ❌ | ❌ |
| **eDB** (Database) | ✅ | 🔨 | 🔨 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **eIPC** (IPC daemon) | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **eBrowser** (Browser) | ✅ | 🔨 | 🔨 | 🔨 | ⚠️ | ✅ | ❌ | ❌ | 🔨 |
| **eOffice** (Productivity) | ✅ | 🔨 | 🔨 | ❌ | ❌ | 🔨 | ❌ | ❌ | ✅ |
| **HealthKey-Ulta** (Health) | ❌ | ❌ | ❌ | 🚧 | ⚠️ | ✅ | ❌ | ❌ | ✅ |
| **eApps** (App Hub) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **www.embeddedos.org** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### 3b. Firmware Target Compatibility

| Firmware | ARM Cortex-M0/M0+ | ARM Cortex-M4/M4F | ARM Cortex-M7 | ARM Cortex-M55 | ARM Cortex-A55 | RISC-V RV32 | Nordic nRF52840 |
|----------|:-----------------:|:-----------------:|:-------------:|:--------------:|:--------------:|:-----------:|:---------------:|
| **eos** | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **eBoot** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **eAI** | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **eosllm** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **eNI** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **ebuild** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HEALTH-BAND-Neuro** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |

### 3c. Runtime Dependency Versions

| Dependency | Minimum | Recommended | Used By |
|------------|---------|-------------|---------|
| Node.js | 20.x | 22.x LTS | eOffice, eDB, eApps, www, eBrowser (web) |
| Python | 3.10 | 3.12 | eVera, EoSim, EoStudio, eDB, eBrowser, HealthKey-Ulta |
| Go | 1.21 | 1.22 | eIPC |
| GCC ARM (`arm-none-eabi-gcc`) | 12.x | 13.x | All firmware |
| CMake | 3.20 | 3.28 | eos, eBoot, eAI, eNI, ebuild, eBrowser |
| Ninja | 1.10 | 1.11 | Firmware (optional) |
| Zephyr SDK | 0.16 | 0.16 | HEALTH-BAND-Neuro |
| Expo / EAS CLI | 0.10 | latest | eVera mobile, eBrowser mobile, HealthKey-Ulta |
| Electron | 28.x | 30.x | eDB, eOffice desktop |
| PyInstaller | 6.x | 6.x | eVera, EoStudio, EoSim Linux builds |
| React Native | 0.73 | 0.74 | HealthKey-Ulta mobile, eVera mobile |

---

## 4. Barriers & Resolution Path

### 4a. Mobile (iOS / Android) Barriers

| Barrier | Affects | Severity | Resolution |
|---------|---------|----------|------------|
| **HealthKey-Ulta `mobile-app/` is empty** (only `.gitignore`) | HealthKey-Ulta Android + iOS | 🔴 Critical | Commit React Native / Expo scaffold into `mobile-app/`; run `npx create-expo-app` or `npx react-native init` |
| **Apple Developer Account required** | All iOS builds (eVera, EoSim, eBrowser, HealthKey-Ulta) | 🔴 Critical | Enroll at [developer.apple.com](https://developer.apple.com) ($99/yr); create provisioning profiles and distribution certificates |
| **EAS project ID not configured** | eVera mobile, eBrowser mobile | 🟡 Medium | Run `eas init` in each `mobile/` directory; commit `eas.json` with project ID |
| **Capacitor sync not run in CI** | EoSim Android + iOS | 🟡 Medium | Add `npx cap sync` step to CI before `./gradlew assembleRelease` |
| **No macOS GitHub Actions runner** | All iOS builds, macOS desktop builds | 🔴 Critical | Add `runs-on: macos-latest` jobs to the workflow for iOS and macOS targets |
| **No Windows GitHub Actions runner** | All Windows desktop builds | 🟡 Medium | Add `runs-on: windows-latest` jobs for PyInstaller/Electron Windows builds |
| **BLE permissions not declared** | eBrowser mobile | 🟡 Medium | Add `android.permissions` for `BLUETOOTH_SCAN`, `BLUETOOTH_CONNECT` in `app.json`; add `NSBluetoothAlwaysUsageDescription` in iOS Info.plist |
| **Google Play signing key** | Android production (AAB) | 🟡 Medium | Generate keystore; store as GitHub secret; configure in `eas.json` |

### 4b. Browser Extension Barriers

| Barrier | Affects | Severity | Resolution |
|---------|---------|----------|------------|
| **`vsce` not installed in CI** | eVera VS Code extension | 🟡 Medium | Add `npm install -g @vscode/vsce` step; run `vsce package` in `vscode-extension/` |
| **Extension packaging not in CI** | eOffice browser, GitHub, JetBrains, Obsidian, Office365 extensions | 🟡 Medium | Add `zip -r` packaging steps for each extension directory in the workflow |
| **Google Workspace OAuth app** | eOffice Google Workspace extension | 🟡 Medium | Create OAuth 2.0 credentials in Google Cloud Console; add `client_id` to manifest |
| **Microsoft 365 manifest signing** | eOffice Office 365 add-in | 🟡 Medium | Register add-in in Azure AD; generate XML manifest with proper GUID |
| **Firefox MV3 compatibility** | All MV3 extensions | 🟠 Low-Med | Firefox supports MV3 from v109+; test `browser_action` vs `action` API differences |
| **Chrome Web Store review** | All Chrome extensions | 🟠 Low | Submit to Chrome Web Store; review takes 1–3 business days |

### 4c. Desktop Build Barriers

| Barrier | Affects | Severity | Resolution |
|---------|---------|----------|------------|
| **Electron packaging not in CI** | eDB, eOffice desktop | 🟡 Medium | Add `electron-builder` step with `--linux AppImage`, `--win`, `--mac` targets |
| **Apple notarization** | All macOS `.dmg` builds | 🔴 Critical | Requires Apple Developer ID cert; use `notarytool` in CI with `APPLE_ID` secret |
| **Windows code signing cert** | All Windows `.exe` builds | 🟡 Medium | Purchase EV code signing cert (DigiCert/Sectigo); configure in Electron Builder |
| **PyInstaller cross-compile not supported** | eVera/EoStudio/EoSim Windows + macOS | 🔴 Critical | Must build on native OS; add `runs-on: windows-latest` and `runs-on: macos-latest` jobs |
| **MSVC toolchain for eBrowser Windows** | eBrowser Windows | 🟡 Medium | Add `runs-on: windows-latest` with `cmake -G "Visual Studio 17 2022"` |

---

*Generated by [eos-stack-manifest](https://github.com/embeddedos-org/eos-stack-manifest) — updated on every release build.*
