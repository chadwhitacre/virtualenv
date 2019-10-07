from __future__ import absolute_import, unicode_literals

import logging
import os
from argparse import ArgumentTypeError


def base_args(options, parser):
    import virtualenv
    from virtualenv.report import LEVELS

    level_map = "|".join("{} - {}".format(c, logging.getLevelName(l)) for c, l in sorted(list(LEVELS.items())))
    parser.add_argument(
        "--version",
        action="version",
        version="{} {}".format(os.path.abspath(virtualenv.__file__), virtualenv.__version__),
    )
    verbosity_group = parser.add_argument_group(
        "verbosity=verbose-quiet, default {}, map {}".format(
            logging.getLevelName(LEVELS[options.verbose - options.quiet]), level_map
        )
    )
    verbosity_exclusive = verbosity_group.add_mutually_exclusive_group()
    verbosity_exclusive.add_argument(
        "-v", "--verbose", action="count", dest="verbose", help="increase verbosity", default=options.verbose
    )
    verbosity_exclusive.add_argument(
        "-q", "--quiet", action="count", dest="quiet", help="decrease verbosity", default=options.quiet
    )
    parser.add_argument(
        "-p",
        "--python",
        dest="python",
        metavar="py",
        help="the python interpreter to replicate(--python=python37 will use the python3.7)",
        default=options.python,
    )


def activation_args(options, parser):
    parser.add_argument(
        "--prompt",
        dest="prompt",
        metavar="prompt",
        help="provides an alternative prompt prefix for this environment",
        default=options.prompt,
    )


def create_args(options, parser):
    parser.add_argument(
        "--clear",
        dest="clear",
        action="store_true",
        help="clear out the non-root install and start from scratch",
        default=options.clear,
    )
    parser.add_argument(
        "--system-site-packages",
        default=options.system_site,
        action="store_true",
        dest="system_site",
        help="Give the virtual environment access to the " "system site-packages dir.",
    )

    parser.add_argument(
        "--no-venv",
        default=options.no_venv,
        action="store_true",
        dest="no_venv",
        help="Do not use venv to create even if the target supports.",
    )

    def validate_dest_dir(value):
        """No path separator in the path and must be write-able"""
        if os.pathsep in value:
            raise ArgumentTypeError(
                "destination {!r} must not contain the path separator ({}) as this would break the activation scripts"
                "".format(value, os.pathsep)
            )
        if os.path.exists(value) and os.path.isfile(value):
            raise ArgumentTypeError("the destination {!r} already exists and is a file".format(value))
        value = dest = os.path.abspath(value)
        while dest:
            if os.path.exists(dest):
                if os.access(dest, os.W_OK):
                    break
                else:
                    non_write_able(dest, value)
            base, _ = os.path.split(dest)
            if base == dest:
                non_write_able(dest, value)  # pragma: no cover
            dest = base
        return value

    def non_write_able(dest, value):
        raise ArgumentTypeError("the destination {!r} is not write-able at {!r}".format(value[len(dest) :], dest))

    parser.add_argument("dest_dir", help="directory to create virtualenv at", type=validate_dest_dir)


def seed_package_args(options, parser):
    seed = parser.add_argument_group("seed packages to be installed after creation")

    seed.add_argument(
        "-s",
        dest="seed_packages",
        metavar="package",
        nargs="+",
        help="specify the seed packages for the virtualenv to be created with (default clears if specified)",
        default=options.seed_packages,
    )
    seed.add_argument(
        "--no-setuptools",
        dest="no_setuptools",
        action="store_true",
        help="do not install setuptools (remove from seed list)",
        default=False,
    )
    seed.add_argument(
        "--no-pip", dest="no_pip", action="store_true", help="do not install pip (remove from seed list)", default=False
    )
    seed.add_argument(
        "--no-wheel",
        dest="no_wheel",
        action="store_true",
        help="do not install wheel (remove from seed list)",
        default=False,
    )
    seed.add_argument(
        "--extra-search-dir",
        dest="search_dirs",
        metavar="dirs",
        action="append",
        help="directories to look for seed package distributions in",
        default=options.search_dirs,
    )
    seed.add_argument(
        "--no-download",
        "--never-download",
        dest="download",
        action="store_false",
        help="do not download pre-installed packages from PyPI (pip/setuptools/wheel only valid seed values)",
        default=options.download,
    )


def make_method(options, parser):
    group_parser = parser.add_argument_group("creation method")
    group = group_parser.add_mutually_exclusive_group()
    group.add_argument(
        "--symlinks",
        default=options.symlinks,
        action="store_true",
        dest="symlinks",
        help="Try to use symlinks rather than copies, " "when symlinks are not the default for " "the platform.",
    )
    group.add_argument(
        "--copies",
        default=not options.symlinks,
        action="store_false",
        dest="symlinks",
        help="Try to use copies rather than symlinks, " "even when symlinks are the default for " "the platform.",
    )
