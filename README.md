# Repos Alfred Workflow

[![GitHub Version][shield-version]][gh-releases]
[![GitHub All Releases][shield-downloads]][gh-releases]
[![GitHub][shield-license]][license-mit]

Browse, search and open local Git repositories with [Alfred][alfred].

<p align="center">
  <img src="img/preview.gif" alt="Repos workflow demo" width="600">
</p>

## Installation

Download the [latest release][gh-latest-release] and open the `.alfredworkflow` file.

After installing, click **Configure Workflow...** in Alfred Preferences to set up your search directories and apps.

## Usage

- `repos [<query>]` — Search your Git repos
  - `↩` — Open in Default App
  - `⌘↩` — Open in Cmd App
  - `⌥↩` — Open in Alt App
  - `^↩` — Open in Ctrl App
  - `⇧↩` — Open in Shift App
  - `fn↩` — Open in Fn App
  - `⇥` — Expand a repo into its worktrees (see below)

### Worktrees

If a repo has git worktrees, press `⇥` (Tab) on it to drill into them. The main worktree is included. `↩` on a worktree opens its path in the configured app, same as opening a regular repo.

Results that can be expanded carry a `(+N worktrees)` hint next to the branch name.

```
Open in GoLand  | 🪾 main (+2 worktrees)  |  ~/code/my-repo

# Tab
Open in GoLand  | 🪾 main             |  ~/code/my-repo
Open in GoLand  | 🪾 feat/login       |  ~/code/my-repo/.worktree/login
Open in GoLand  | 🪾 wt/experiment    |  ~/code/my-repo/.worktree/experiment
```

## Configuration

Open **Configure Workflow...** in Alfred Preferences. No config files to mess with, and your settings sync across machines via Alfred Sync.

### Apps

Each modifier key has a dropdown with these modes:

| Mode | What it does |
|------|-------------|
| None | Disabled |
| Finder | Reveals the repo folder |
| Terminal | Opens in Terminal.app |
| Default Browser | Opens the repo's remote URL |
| Custom App | Pick any `.app` via the file picker below it |

If you pick a browser app (Chrome, Safari, Firefox, Arc, etc.) as a custom app, the workflow will open the remote URL instead of the local path.

The `Remote Name` field controls which git remote is used for browser URLs. Defaults to `origin`.

### Search directories

You get 5 slots. Each one has:

- A folder picker for the directory to scan
- `Depth` controls how many levels deep to search. Default is `2`, which means repos should be direct children of the search directory.
- `Excludes` takes comma-separated glob patterns to skip (e.g. `tmp, vendor`)
- `Name for Parent` controls which directory level shows as the repo name. `1` is the folder containing `.git` (the default), `2` is its parent, etc. Useful when all your repos have the same inner folder name like `src`.

### Advanced

- `Global Exclude Patterns` skips matching directories across all search paths, one pattern per line
- `Refresh Interval` is how old the repo cache can get (in seconds) before a background refresh kicks in on the next picker open. Default `30`. The refresh runs while you search and fresh results swap in-place.

### Custom icons

Drop a `.alfred-repos-icon.png` file in a directory and all repos under it will use that icon in Alfred results. For example, `~/code/github/.alfred-repos-icon.png` applies to everything in `~/code/github/`.

## Issues

File bugs or feature requests on [GitHub issues][gh-issues].

## Credits

Fork of [harrtho/alfred-repos](https://github.com/harrtho/alfred-repos) by [Thomas Harr](https://github.com/harrtho), which continued the [original workflow](https://github.com/deanishe/alfred-repos) by [Dean Jackson](https://github.com/deanishe).

## License

[MIT][license-mit]

Libraries: [docopt][docopt] (MIT), [Alfred-PyWorkflow][alfred-pyworkflow] (MIT)

Icons from [git-scm.com][git] ([CC BY 3.0][license-cc])

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
