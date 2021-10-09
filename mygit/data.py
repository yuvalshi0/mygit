import hashlib
import os
from collections import namedtuple

MYGIT_DIR = ".mygit"
RefValue = namedtuple("RefValue", ["symbolic", "value"])


def init():
    os.makedirs(MYGIT_DIR)
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


def update_ref(ref, value):
    assert not value.symbolic
    ref_path = "{}/{}".format(MYGIT_DIR, ref)
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, "w") as f:
        f.write(value.value)


def get_ref(ref):
    ref_path = "{}/{}".format(MYGIT_DIR, ref)
    value = None
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            value = f.read().strip()

    if value and value.startswith("ref:"):
        return get_ref(value.split(":", 1)[1].strip())

    return RefValue(symbolic=False, value=value)


def iter_refs():
    refs = ["HEAD"]
    for root, _, filenames in os.walk("{}/refs/".format(MYGIT_DIR)):
        root = os.path.relpath(root, MYGIT_DIR)
        refs.extend("{}/{}".format(root, name) for name in filenames)

    for refname in refs:
        yield refname, get_ref(refname)
