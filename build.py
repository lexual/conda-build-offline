import glob
import os

import conda_build
import conda_build.api


def main():
    to_skip = [
        'jsoncpp',
        'pip',
        'wheel',
        'auto',
        'python',
        'perl',
        'setuptools',
        'pkg-config',
        'automake',
        'autoconf',
    ]
    pys = ['27', '36']
    for py in pys:
        os.environ['CONDA_NPY'] = '112'
        os.environ['CONDA_PY'] = '27'
        for recipe in glob.glob('forks/*-feedstock/recipe/meta.yaml'):
            rendered = conda_build.api.render(recipe)[0]
            pkg = rendered.get_value('package/name')
            print(pkg)
            path = conda_build.api.get_output_file_path(recipe)
            print(path)
            if pkg in to_skip:
                continue
            elif not os.path.exists(path):
                try:
                    conda_build.api.build(recipe)
                except:
                    pass


if __name__ == '__main__':
    main()
