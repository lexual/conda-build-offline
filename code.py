import argparse
import logging
import os

from glob import glob

from conda_build import api
from pprint import pprint
import git
import github


logger = logging.getLogger(__name__)


def main_new():
    fetched = set()
    parser = argparse.ArgumentParser()
    parser.add_argument('pkgs', nargs='+')
    args = parser.parse_args()
    for pkg in args.pkgs:
        fetch_feedstock(pkg, 'forks')
        fetched.add(pkg)
    max_dependency_levels = 10
    for i in range(15):
        print(i, 'x' * 33)
        deps = render_requirements('forks')
        print(deps)
        to_fetch = deps - fetched
        if not to_fetch:
            print('print all done!!!')
            break
        logger.info('to_fetch', to_fetch)
        for pkg in to_fetch:
            if pkg == 'proj4':
                pkg = 'proj.4'
            elif pkg == 'decorator':
                pkg = 'python-decorator'
            elif pkg == 'pathlib2':
                pkg = 'python-pathlib2'
            elif pkg == 'simplegeneric':
                pkg = 'python-simplegeneric'
            fetch_feedstock(pkg, 'forks')
            fetched.add(pkg)


def render_requirements(folder):
    deps = set()
    for recipe in glob('{folder}/*/recipe/meta.yaml'.format(folder=folder)):
        requirements = api.render(recipe)[0].meta['requirements']
        run_deps = [dep.split(' ')[0] for dep in requirements.get('run', [])]
        build_deps = [dep.split(' ')[0] for dep in requirements.get('build', [])]
        deps.update(run_deps + build_deps)
    return deps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest')
    args = parser.parse_args()
    with open(args.manifest) as f:
        for i, line in enumerate(f):
            if 'conda-forge' not in line:
                continue
            if line.startswith('#'):
                continue
            pkg_part = line.split()[1]
            pkg = pkg_part.rsplit('-', 2)[0]
            if pkg == 'proj4':
                pkg = 'proj.4'
            #if 'qt' in pkg:
            #    continue
            logger.info(pkg)
            fetch_feedstock(pkg, folder)


def fetch_feedstock(pkg, folder):
    if pkg in ('gcc', 'libgcc', 'cryptography', 'util-linux'):
        return
    print(pkg)
    logger.info('fetching ' + pkg)
    url = 'git@github.com:lexual/{pkg}-feedstock.git'.format(pkg=pkg)
    local_dir = os.path.join(folder, pkg + '-feedstock')
    if not os.path.exists(local_dir):
        make_fork(pkg)
        git.Repo.clone_from(url, local_dir)
    repo = git.Repo.init(local_dir)
    branch = 'master'
    if pkg == 'python':
        branch = '2.7'
    elif pkg == 'ncurses':
        branch = 'issue033_support_newer_condabuild'
    elif pkg == 'patchelf':
        branch = 'fix_md5sum'
    elif pkg == 'matplotlib':
        branch = 'bom'
    repo.remotes['origin'].fetch()
    repo.git.checkout(branch)
    if pkg in ('ncurses', 'matplotlib', 'patchelf'):
        return repo
    create_remote(repo, 'conda-forge', get_forge_url(pkg))
    repo.remotes['conda-forge'].pull(branch)
    repo.remotes['origin'].push(branch)
    return repo


def create_remote(repo, name, url):
    try:
        repo.remotes['conda-forge']
    except IndexError:
        forge_remote = repo.create_remote('conda-forge', url)


def make_fork(pkg):
    password = os.environ['GITHUB_PASSWORD']
    g = github.Github('lexual', password)
    try:
        g.get_user().get_repo(pkg + '-feedstock')
    except github.GithubException:
        g.get_user().create_fork(g.get_repo('conda-forge/{}-feedstock'.format(pkg)))


def get_forge_url(pkg):
    forge_url = 'git@github.com:conda-forge/{pkg}-feedstock.git'.format(pkg=pkg)
    return forge_url


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #main()
    main_new()
