import hashlib
import os

MYGIT_DIR = ".mygit"


def init():
    os.mkdir(MYGIT_DIR)
    os.makedirs("{}/objects".format(MYGIT_DIR))


def hash_object(data, type_="blob"):
    oid = hashlib.sha1(data).hexdigest()
    obj = type_.encode() + b"\x00" + data
    with open("{}/objects/{}".format(MYGIT_DIR, oid), "wb") as out:
        out.write(obj)
    return oid


def get_object(oid, expected="blob"):
    with open("{}/objects/{}".format(MYGIT_DIR, oid), "rb") as f:
        obj = f.read()

    type_, _, content = obj.partition(b"\x00")
    type_ = type_.decode()

    if expected is not None:
        assert type_ == expected, "Expected {}, got {}".format(expected, type_)
    return content


def set_HEAD(oid):
    with open("{}/HEAD".format(MYGIT_DIR), "w") as f:
        f.write(oid)


def get_HEAD():
    if os.path.isfile("{}/HEAD".format(MYGIT_DIR)):
        with open("{}/HEAD".format(MYGIT_DIR)) as f:
            return f.read().strip()
