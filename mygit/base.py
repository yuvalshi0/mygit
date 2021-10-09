import itertools
import operator
import os
from collections import namedtuple

from . import data

Commit = namedtuple("Commit", ["tree", "parent", "message"])


def write_tree(directory="."):
    entries = []
    with os.scandir(directory) as it:
        for entry in it:
            full = "{}/{}".format(directory, entry.name)
            if is_ignored(full):
                continue  # skip mygit files
            if entry.is_file(follow_symlinks=False):
                type_ = "blob"
                with open(full, "rb") as f:  # write object
                    oid = data.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                type_ = "tree"
                oid = write_tree(full)
            entries.append((entry.name, oid, type_))

        tree = "".join(
            "{} {} {}\n".format(name, oid, type_)
            for name, oid, type_ in sorted(entries)
        )
    return data.hash_object(tree.encode(), "tree")


def _iter_tree_entries(oid):
    if not oid:
        return
    tree = data.get_object(oid, "tree")
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(" ", 2)
        yield type_, oid, name


def get_tree(oid, base_path=""):
    result = {}
    for type_, oid, name in _iter_tree_entries(oid):
        assert "/" not in name
        assert name not in ("..", ".")
        path = base_path + name
        if type_ == "blob":
            result[path] = oid
        elif type_ == "tree":
            result.update(get_tree(oid, f"{path}/"))
        else:
            assert False, "Unknown tree entry {}".format(type_)
    return result


def read_tree(tree_oid):
    _empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path="./").items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data.get_object(oid))


def _empty_current_directory():
    for root, dirnames, filenames in os.walk(".", topdown=False):
        for filename in filenames:
            path = os.path.relpath("{}/{}".format(root, filename))
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)
        for dirname in dirnames:
            path = os.path.relpath("{}/{}".format(root, dirname))
            if is_ignored(path):
                continue
            try:
                os.rmdir(path)
            except (FileNotFoundError, OSError):
                # deletion might fail if the directory contains ignored files,
                pass


def checkout(oid):
    commit = get_commit(oid)
    read_tree(commit.tree)
    data.set_HEAD(oid)


def commit(message):
    commit = "tree {}\n".format(write_tree())
    commit += "\n"
    commit += "{}\n".format(message)

    HEAD = data.get_HEAD()
    if HEAD:  # save parent commit
        commit += "parent {}\n".format(HEAD)

    oid = data.hash_object(commit.encode(), "commit")

    data.set_HEAD(oid)

    return oid


def create_tag(name, oid):
    # TODO Actually create the tag
    pass


def get_commit(oid):
    parent = None

    commit = data.get_object(oid, "commit").decode()
    lines = iter(commit.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(" ", 1)
        if key == "tree":
            tree = value
        elif key == "parent":
            parent = value
        else:
            assert False, "Unknown field {}".format(key)

    message = "\n".join(lines)
    return Commit(tree=tree, parent=parent, message=message)


def is_ignored(path):
    return ".mygit" in path.split("/")
