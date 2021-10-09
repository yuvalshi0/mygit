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


def update_ref(ref, value, deref=True):
    ref = _get_ref_internal(ref, deref)[0]

    assert value.value
    if value.symbolic:
        value = "ref: {}".format(value.value)
    else:
        value = value.value

    ref_path = "{}/{}".format(MYGIT_DIR, ref)
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, "w") as f:
        f.write(value)


def get_ref(ref, deref=True):
    return _get_ref_internal(ref, deref)[1]


def _get_ref_internal(ref, deref):
    ref_path = "{}/{}".format(MYGIT_DIR, ref)
    value = None
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            value = f.read().strip()

    symbolic = bool(value) and value.startswith("ref:")
    if symbolic:
        value = value.split(":", 1)[1].strip()
        if deref:
            return _get_ref_internal(value, deref=True)

    return ref, RefValue(symbolic=symbolic, value=value)


def iter_refs(prefix="", deref=True):
    refs = ["HEAD"]
    for root, _, filenames in os.walk("{}/refs/".format(MYGIT_DIR)):
        root = os.path.relpath(root, MYGIT_DIR)
        refs.extend("{}/{}".format(root, name) for name in filenames)

    for refname in refs:
        if not refname.startswith(prefix):
            continue
        yield refname, get_ref(refname, deref=deref)
