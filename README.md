# Repos Alfred Workflow

[![GitHub Version][shield-version]][gh-releases]
[![GitHub All Releases][shield-downloads]][gh-releases]
[![GitHub][shield-license]][license-mit]

Browse, search and open local Git repositories with [Alfred][alfred].

<p align="center">
  <img src="img/preview.gif" alt="Repos workflow demo" width="600">
</p>

## Download & Installation

Download the [latest workflow release][gh-latest-release] from GitHub. Open the workflow file to
install in Alfred.

## Getting Started

1. Open Alfred Preferences and find the **Repos** workflow
2. Click **Configure Workflow...** to open the configuration panel
3. Under 🖥️ pick how you want to open repos for each modifier key
4. Under 📂 add at least one folder that contains your Git repos
5. Type `repos` in Alfred and start searching!

## Usage

- `repos [<query>]` — Search your Git repositories
  - `↩` — Open in Default App
  - `⌘↩` — Open in Cmd App
  - `⌥↩` — Open in Alt App
  - `^↩` — Open in Ctrl App
  - `⇧↩` — Open in Shift App
  - `fn↩` — Open in Fn App
- `reposupdate` — Force refresh the cached list of repositories
- `reposhelp` — Open this README in your browser

## Configuration

All settings are configured via Alfred's native **Configure Workflow...** UI. No manual file editing required. Settings are synced automatically via Alfred Sync.

### 🖥️ App Configuration

Each modifier key can be set to one of:

| Mode | Behavior |
|------|----------|
| **None** | Modifier key disabled |
| **Finder** | Reveal repo folder in Finder |
| **Terminal** | Open repo in Terminal.app |
| **Default Browser** | Open the repo's remote URL in your default browser |
| **Custom App** | Pick any `.app` via the companion file picker |

If a custom app is a recognized browser (Chrome, Safari, Firefox, Arc, Brave, Edge, Opera, Vivaldi), it will automatically open the remote URL instead of the local path.

**Remote Name** controls which git remote is used for browser URLs (default: `origin`).

### 📂 Search Directories

Up to 5 search directory slots are available. Each slot has:

- **Search Directory** — Folder to scan for Git repos
- **Depth** — How many levels deep to search (default: `2`). A depth of `2` means repos must be direct children of the search directory.
- **Excludes** — Comma-separated glob patterns to skip (e.g. `tmp, vendor, node_modules`)
- **Name for Parent** — Which directory level to use as the repo name (`1` = immediate parent of `.git`, `2` = grandparent, etc.)

### ⚙️ Advanced

- **Global Exclude Patterns** — Glob patterns to exclude from ALL search directories, one per line
- **Update Interval** — Minutes between automatic repo list updates (default: `180` = 3 hours). Use `reposupdate` to refresh immediately.

### Custom Repo Icons

Place a file named `.alfred-repos-icon.png` in the parent directory of your repos to give them a custom icon in Alfred results.

For example, if your repos live in `~/code/github/`, place the icon at `~/code/github/.alfred-repos-icon.png`. All repos under that directory will display the custom icon.

## Bug Reports and Feature Requests

Please use [GitHub issues][gh-issues] to report bugs or request features.

## Contributors

This Alfred Workflow is a fork of [harrtho/alfred-repos](https://github.com/harrtho/alfred-repos) by [Thomas Harr](https://github.com/harrtho), which itself continued the [abandoned workflow](https://github.com/deanishe/alfred-repos) by [Dean Jackson](https://github.com/deanishe).

## License

Repos Alfred Workflow is licensed under the [MIT License][license-mit]

The workflow uses the following libraries:

- [docopt][docopt] ([MIT License][license-docopt])
- [Alfred-PyWorkflow][alfred-pyworkflow] ([MIT License][license-mit])

The workflow uses the following icons:

- [git-scm.com][git] ([Creative Commons Attribution 3.0 Unported License][license-cc])

[alfred-pyworkflow]: https://github.com/harrtho/alfred-pyworkflow
[alfred]: https://www.alfredapp.com
[docopt]: https://github.com/docopt/docopt
[gh-issues]: https://github.com/sherifabdlnaby/alfred-repos/issues
[gh-latest-release]: https://github.com/sherifabdlnaby/alfred-repos/releases/latest
[gh-releases]: https://github.com/sherifabdlnaby/alfred-repos/releases
[git]: https://git-scm.com/downloads/logos
[license-cc]: https://creativecommons.org/licenses/by/3.0/
[license-docopt]: https://github.com/docopt/docopt/blob/master/LICENSE-MIT
[license-mit]: https://opensource.org/licenses/MIT
[shield-downloads]: https://img.shields.io/github/downloads/sherifabdlnaby/alfred-repos/total.svg
[shield-license]: https://img.shields.io/github/license/sherifabdlnaby/alfred-repos.svg
[shield-version]: https://img.shields.io/github/release/sherifabdlnaby/alfred-repos.svg
