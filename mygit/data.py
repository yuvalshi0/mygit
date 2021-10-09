import hashlib
import os

MYGIT_DIR = ".mygit"


def init():
    """
    Creates the mygit directory tree needed for initializing a repository
    """
    os.mkdirs(MYGIT_DIR)
    os.makedirs("{}/objects".format(MYGIT_DIR))


def hash_object(data):
    """
    Hashes a file objects, saves it in the repo object directory and returns the hash result
    """
    oid = hashlib.sha1(data).hexdigest()
    with open(f"{MYGIT_DIR}/objects/{oid}", "wb") as out:
        out.write(data)
    return oid
