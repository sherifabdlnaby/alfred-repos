#!/usr/bin/env python3
# encoding: utf-8
#
# Copyright (c) 2026 Sherif Abdel-Naby <sherifabdlnaby@gmail.com>
# Copyright (c) 2022 Thomas Harr <xDevThomas@gmail.com>
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2013-11-04
#

"""repos.py [command] [options] [<query>] [<path>]

Find, open and search Git repos on your system.

Usage:
    repos.py search [<query>]
    repos.py update
    repos.py open <appkey> <path>

Options:
    -h, --help      Show this message

"""


import hashlib
import json
import os
import re
import subprocess
import sys
from collections import namedtuple

from workflow import ICON_INFO, ICON_WARNING, Workflow
from workflow.background import is_running, run_in_background
from workflow.update import Version
from workflow.notify import notify

DEFAULT_UPDATE_INTERVAL = 15  # minutes

UPDATE_SETTINGS = {'github_slug': 'sherifabdlnaby/alfred-repos'}

HELP_URL = 'https://github.com/sherifabdlnaby/alfred-repos/issues'

ICON_UPDATE = 'update-available.png'

BROWSERS = {
    'Google Chrome',
    'Firefox',
    'Safari',
    'WebKit',
    'Arc',
    'Brave Browser',
    'Microsoft Edge',
    'Opera',
    'Vivaldi',
}

# App open modes (popupbutton values)
MODE_NONE = 'none'
MODE_FINDER = 'finder'
MODE_TERMINAL = 'terminal'
MODE_BROWSER = 'browser'
MODE_CUSTOM = 'custom'

NUM_SEARCH_SLOTS = 5

BRANCH_ICON = '🪾'

log = None


Repo = namedtuple('Repo', 'name path branch worktrees')
Worktree = namedtuple('Worktree', 'name path branch')


class AttrDict(dict):
    """Access dictionary keys as attributes."""

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def get_search_dirs_from_env():
    """Build search_dirs list from Alfred User Configuration env vars."""
    dirs = []
    for i in range(1, NUM_SEARCH_SLOTS + 1):
        path = os.getenv(f'search_dir_{i}', '').strip()
        if not path:
            continue
        excludes_raw = os.getenv(f'search_excludes_{i}', '')
        dirs.append({
            'path': path,
            'depth': int(os.getenv(f'search_depth_{i}', '2') or '2'),
            'excludes': [x.strip() for x in excludes_raw.split(',') if x.strip()],
            'name_for_parent': int(os.getenv(f'search_name_for_parent_{i}', '1') or '1'),
        })
    return dirs


def get_global_excludes():
    """Read global exclude patterns from env var (newline-separated)."""
    raw = os.getenv('global_excludes', '').strip()
    if not raw:
        return []
    return [x.strip() for x in raw.splitlines() if x.strip()]


def search_config_hash(search_dirs, global_excludes):
    """Compute a hash from the already-parsed search config."""
    blob = json.dumps({'dirs': search_dirs, 'excludes': global_excludes}, sort_keys=True)
    return hashlib.md5(blob.encode()).hexdigest()


def config_changed(search_dirs, global_excludes):
    """Check if search config changed since last cache update.

    Does NOT write the new hash to cache. The caller should persist
    the hash after a successful update via save_config_hash().
    """
    current = search_config_hash(search_dirs, global_excludes)
    stored = wf.cached_data('config_hash', max_age=0)
    return current != stored


def save_config_hash(search_dirs, global_excludes):
    """Persist the config hash after a successful update."""
    wf.cache_data('config_hash', search_config_hash(search_dirs, global_excludes))


def app_name_from_path(app_path):
    """Extract display name from an .app path.

    '/Applications/Visual Studio Code.app' -> 'Visual Studio Code'
    """
    return os.path.basename(app_path).removesuffix('.app')


def app_display_name(mode, path=''):
    """Return a human-readable name for an app config."""
    if mode == MODE_FINDER:
        return 'Finder'
    if mode == MODE_TERMINAL:
        return 'Terminal'
    if mode == MODE_BROWSER:
        return 'Default Browser'
    if mode == MODE_CUSTOM and path:
        return app_name_from_path(path)
    return None


def is_browser(app_path):
    """Check if the app is a web browser by its name."""
    return app_name_from_path(app_path) in BROWSERS


def get_apps():
    """Load app configs from Alfred User Configuration env vars.

    Each modifier key has a mode (popupbutton) and optional path (filepicker).

    Returns:
        dict: Modkey to (mode, path) tuple mapping. Keys with mode 'none' are excluded.

    """
    apps = {}
    for key in ('default', 'cmd', 'alt', 'ctrl', 'shift', 'fn'):
        mode = os.getenv(f'app_{key}', MODE_NONE).strip()
        path = os.getenv(f'app_{key}_path', '').strip()
        if mode and mode != MODE_NONE:
            apps[key] = (mode, path)

    if 'default' not in apps:
        apps['default'] = (MODE_FINDER, '')

    return apps


def get_repos(opts):
    """Load repos from cache, triggering an update if necessary.

    Args:
        opts (AttrDict): CLI options

    Returns:
        list: Sequence of `Repo` tuples.

    """
    if not wf.cached_data_fresh('repos_v2', max_age=opts.update_interval):
        do_update()
    repos = wf.cached_data('repos_v2', max_age=0)

    if not repos:
        do_update()
        return []

    if isinstance(repos[0], str):
        do_update()
        return []

    return repos


def repo_url(path):
    """Return repo URL extracted from `.git/config`.

    Args:
        path (str): Path to git repo.

    Returns:
        str: URL of remote. Defaults to origin.

    """
    remote_name = os.getenv('remote_name', 'origin').strip() or 'origin'

    remotes = subprocess.check_output(['git', 'remote'], cwd=path).decode('utf-8').splitlines()
    log.debug('remotes=%s', remotes)
    if remote_name not in remotes:
        notify('No remote named {}'.format(remote_name), 'Check your settings', 'Available remotes: {}'.format(', '.join(remotes)), 'Sosumi')
        log.error('No remote named %s in %s', remote_name, path)
        return None

    url = subprocess.check_output(['git', 'config', 'remote.' + remote_name + '.url'],
                                  cwd=path).decode('utf-8')
    url = re.sub(r'(^.+@)|(^https://)|(^git://)|(.git$)', '', url)
    return 'https://' + re.sub(r':', '/', url).strip()


def get_branch(path):
    """Return current branch name (or short SHA for detached HEAD) by reading
    `.git/HEAD` directly. Returns None if unresolvable.

    Avoids spawning `git` per repo, so it's safe to call during search.
    Handles `.git` files (worktrees, submodules) by following `gitdir:`.
    """
    git_path = os.path.join(path, '.git')
    try:
        if os.path.isfile(git_path):
            with open(git_path) as f:
                line = f.readline().strip()
            if not line.startswith('gitdir: '):
                return None
            gitdir = line[len('gitdir: '):]
            git_path = gitdir if os.path.isabs(gitdir) else os.path.join(path, gitdir)

        with open(os.path.join(git_path, 'HEAD')) as f:
            head = f.readline().strip()

        if head.startswith('ref: refs/heads/'):
            return head[len('ref: refs/heads/'):]
        return head[:7] if head else None
    except OSError:
        return None


def enumerate_worktrees(repo_path):
    """List linked worktrees under `<repo>/.git/worktrees/`. Empty if none.

    Main worktree is excluded; callers synthesize it from the Repo fields.
    """
    worktrees_dir = os.path.join(repo_path, '.git', 'worktrees')
    try:
        entries = sorted(os.scandir(worktrees_dir), key=lambda e: e.name)
    except (OSError, NotADirectoryError):
        return []

    out = []
    for entry in entries:
        try:
            with open(os.path.join(entry.path, 'gitdir')) as f:
                gitdir = f.readline().strip()
        except OSError:
            continue
        wt_path = os.path.dirname(gitdir)
        wt_branch = get_branch(wt_path) or entry.name
        out.append(Worktree(wt_branch, wt_path, wt_branch))
    return out


def _resolve_open_target(mode, custom_path, repo_path):
    """Determine the target and app flag for opening a repo.

    Returns:
        tuple: (target, app_flag_list) or None if nothing to open.
    """
    use_url = mode == MODE_BROWSER or (mode == MODE_CUSTOM and custom_path and is_browser(custom_path))

    if use_url:
        target = repo_url(repo_path)
        if not target:
            return None
    else:
        target = repo_path

    if mode == MODE_FINDER:
        app_flag = []
    elif mode == MODE_TERMINAL:
        app_flag = ['-a', 'Terminal']
    elif mode == MODE_BROWSER:
        app_flag = []
    elif mode == MODE_CUSTOM and custom_path:
        app_flag = ['-a', custom_path]
    else:
        return None

    return target, app_flag


def do_open(opts):
    """Open repo in the specified application.

    Args:
        opts (AttrDict): CLI options.

    Returns:
        int: Exit status.

    """
    all_apps = get_apps()
    app = all_apps.get(opts.appkey)
    if app is None:
        print('App {} not set. Configure this workflow in Alfred Preferences.'.format(opts.appkey))
        return 0

    mode, path = app
    result = _resolve_open_target(mode, path, opts.path)
    if result:
        target, app_flag = result
        log.info('opening %s ...', target)
        subprocess.call(['open'] + app_flag + [target])


def do_update():
    """Update cached list of git repos."""
    run_in_background('update', ['/usr/bin/env', 'python3', 'update.py'])
    return 0


def do_search(repos, opts):
    """Filter list of repos and show results in Alfred.

    Args:
        repos (list): Sequence of ``Repo`` tuples.
        opts (AttrDict): CLI options.

    Returns:
        int: Exit status.

    """
    apps = get_apps()
    subtitles = {}
    valid = {}
    for key, (mode, path) in apps.items():
        name = app_display_name(mode, path)
        if name:
            subtitles[key] = 'Open in {}'.format(name)
            valid[key] = True
        else:
            subtitles[key] = ('App for ' + key + ' not set. '
                              'Configure this workflow in Alfred Preferences.')
            valid[key] = False

    if wf.cached_data_age('repos_v2') > 30 and not is_running('update'):
        run_in_background('update', ['/usr/bin/env', 'python3', 'update.py'])
        wf.rerun = 2.0

    query = opts.query
    expanded = None
    if '/' in query:
        prefix, rest = query.split('/', 1)
        matches = [r for r in repos if r.name == prefix]
        if len(matches) == 1:
            expanded = matches[0]
            query = rest

    if expanded:
        items = [Worktree(expanded.branch or expanded.name, expanded.path, expanded.branch)]
        items += expanded.worktrees
    else:
        items = repos

    if query:
        items = wf.filter(query, items, lambda t: t[0], min_score=30)
        log.info('%d match `%s`', len(items), query)

    if not items:
        wf.add_item('No matching worktrees found' if expanded else 'No matching repos found',
                    icon=ICON_WARNING)

    home = os.environ['HOME']
    for r in items:
        log.debug(r)
        pretty_path = r.path.replace(home, '~')
        wt_count = len(r.worktrees) if hasattr(r, 'worktrees') else 0
        wt_hint = ' (+{} worktree{})'.format(wt_count, '' if wt_count == 1 else 's') \
            if (not expanded and wt_count) else ''
        branch_info = '{} {}{}  |  '.format(BRANCH_ICON, r.branch, wt_hint) if r.branch else ''

        icon = 'icon.png'
        if os.path.isfile(os.path.dirname(r.path) + '/' + '.alfred-repos-icon.png'):
            icon = os.path.dirname(r.path) + '/' + '.alfred-repos-icon.png'

        def compose(app_subtitle):
            sep = '  | ' if branch_info else '  |  '
            return '{}{}{}{}'.format(app_subtitle, sep, branch_info, pretty_path)

        it = wf.add_item(
            r.name,
            compose(subtitles.get('default', '')),
            arg=r.path,
            uid=r.path,
            valid=valid.get('default', False),
            type='file',
            icon=icon,
            autocomplete=(r.name + '/') if (not expanded and wt_count) else None,
        )
        it.setvar('appkey', 'default')

        for key in apps:
            if key == 'default':
                continue
            mod = it.add_modifier(key.replace('_', '+'),
                                  compose(subtitles[key]),
                                  arg=r.path, valid=valid[key])
            mod.setvar('appkey', key)

    wf.send_feedback()
    return 0


def parse_args():
    """Extract options from CLI arguments.

    Returns:
        AttrDict: CLI options.

    """
    from docopt import docopt

    args = docopt(__doc__, wf.args)

    log.debug('args=%r', args)

    update_interval = int(os.getenv('update_interval',
                                    str(DEFAULT_UPDATE_INTERVAL))) * 60

    opts = AttrDict(
        query=(args.get('<query>') or '').strip(),
        path=args.get('<path>'),
        appkey=args.get('<appkey>') or 'default',
        update_interval=update_interval,
        do_search=args.get('search'),
        do_update=args.get('update'),
        do_open=args.get('open'),
    )

    log.debug('opts=%r', opts)
    return opts


def main(wf):
    """Run the workflow."""
    opts = parse_args()

    if opts.do_open:
        return do_open(opts)

    elif opts.do_update:
        return do_update()

    if wf.update_available:
        wf.add_item('Workflow Update is Available',
                    '↩ or ⇥ to install',
                    autocomplete='workflow:update',
                    valid=False,
                    icon=ICON_UPDATE)

    search_dirs = get_search_dirs_from_env()

    if not search_dirs:
        wf.add_item("No search directories configured",
                    'Configure this workflow in Alfred Preferences',
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    global_excludes = get_global_excludes()
    if config_changed(search_dirs, global_excludes):
        log.info('config was updated. Reloading repos...')
        do_update()

    repos = get_repos(opts)

    if not repos:
        if is_running('update'):
            wf.add_item('Updating list of repos…',
                        'Should be done in a few seconds',
                        icon=ICON_INFO)
            wf.rerun = 0.5
        else:
            wf.add_item('No git repos found',
                        'Check your search directories in Alfred Preferences',
                        icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    if is_running('update'):
        wf.rerun = 0.5

    return do_search(repos, opts)


if __name__ == '__main__':
    wf = Workflow(update_settings=UPDATE_SETTINGS,
                  help_url=HELP_URL)
    log = wf.logger
    sys.exit(wf.run(main))
