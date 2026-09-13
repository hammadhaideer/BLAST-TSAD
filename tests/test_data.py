import zipfile
from pathlib import Path

import numpy as np

from blast.data import read_features_label_free, train_index_from_name


def test_train_index_parser():
    assert train_index_from_name("001_X_id_1_Sensor_tr_4055_1st_5000.csv") == 4055


def test_label_free_reader_never_needs_label_to_be_numeric(tmp_path: Path):
    archive = tmp_path / "toy.zip"
    member = "TSB-AD-M/toy.csv"
    payload = b"f1,f2,label\n1.0,2.0,DO_NOT_PARSE\n3.0,4.0,STILL_OPAQUE\n"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(member, payload)

    with zipfile.ZipFile(archive) as zf:
        x, names = read_features_label_free(zf, "TSB-AD-M", "toy.csv")

    assert names == ["f1", "f2"]
    np.testing.assert_allclose(x, [[1.0, 2.0], [3.0, 4.0]])
