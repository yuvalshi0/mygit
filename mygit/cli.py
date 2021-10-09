import argparse
import os
import sys
import textwrap

from . import base, data


def main():
    """
    Main CLI function
    """
    args = parse_args()
    args.func(args)


def parse_args():
    """
    Args parser
    """
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    oid = base.get_oid

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser("hash-object")
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file")

    cat_file_parser = commands.add_parser("cat-file")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("object", type=oid)

    write_tree_parser = commands.add_parser("write-tree")
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser("read-tree")
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree", type=oid)

    commit_parser = commands.add_parser("commit")
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument("-m", "--message", required=True)

    log_parser = commands.add_parser("log")
    log_parser.set_defaults(func=log)
    log_parser.add_argument("oid", type=oid, nargs="?", default="@")

    checkout_parser = commands.add_parser("checkout")
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument("oid", type=oid)

    tag_parser = commands.add_parser("tag")
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument("name")
    tag_parser.add_argument("oid", type=oid, nargs="?", default="@")

    return parser.parse_args()


def init(args):
    data.init()
    print(
        "Initialized empty mygit repository in {}/{}".format(
            os.getcwd(), data.MYGIT_DIR
        )
    )


def hash_object(args):
    with open(args.file, "rb") as f:
        print(data.hash_object(f.read()))


def cat_file(args):
    sys.stdout.flush()  # clear the stdout
    sys.stdout.buffer.write(
        data.get_object(args.object, expected=None)
    )  # write the file content


def write_tree(args):
    print(base.write_tree())


def read_tree(args):
    base.read_tree(args.tree)


def commit(args):
    print(base.commit(args.message))


def log(args):
    oid = args.oid
    while oid:
        commit = base.get_commit(oid)

        print("commit {}\n".format(oid))
        print(textwrap.indent(commit.message, "    "))
        print("")

        oid = commit.parent


def checkout(args):
    base.checkout(args.oid)


def tag(args):
    oid = args.oid
    base.create_tag(args.name, oid)
