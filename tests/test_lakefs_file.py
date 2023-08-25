from lakefs_spec import LakeFSFileSystem
from tests.conftest import LakeFSOptions
from tests.util import RandomFileFactory


def test_lakefs_file_open_read(
    lakefs_options: LakeFSOptions,
    repository: str,
    temp_branch: str,
    random_file_factory: RandomFileFactory,
) -> None:
    random_file = random_file_factory.make()
    with open(random_file, "rb") as f:
        orig_text = f.read()

    fs = LakeFSFileSystem(
        host=lakefs_options.host,
        username=lakefs_options.username,
        password=lakefs_options.password,
    )

    lpath = str(random_file)
    rpath = f"{repository}/{temp_branch}/{random_file.name}"
    fs.put_file(lpath, rpath)

    # try opening the remote file
    with fs.open(rpath) as fp:
        text = fp.read()

    assert text == orig_text


def test_lakefs_file_open_write(
    lakefs_options: LakeFSOptions,
    repository: str,
    temp_branch: str,
    random_file_factory: RandomFileFactory,
) -> None:
    random_file = random_file_factory.make()
    with open(random_file, "rb") as f:
        orig_text = f.read()

    fs = LakeFSFileSystem(
        host=lakefs_options.host,
        username=lakefs_options.username,
        password=lakefs_options.password,
    )
    rpath = f"{repository}/{temp_branch}/{random_file.name}"

    # try opening the remote file and writing to it
    with fs.open(rpath, "wb") as fp:
        fp.write(orig_text)

    # pulling the written file down again, using ONLY built-in open (!)
    lpath = random_file.with_name(random_file.name + "_copy")
    fs.get(rpath, str(lpath))

    with open(lpath, "rb") as f:
        new_text = f.read()

    # round-trip assert.
    assert new_text == orig_text
