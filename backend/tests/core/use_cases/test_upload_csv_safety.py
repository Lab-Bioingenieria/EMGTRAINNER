import hashlib
from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import UploadFile

from core.use_cases.upload_csv import UploadCSV

VALID_CSV = b"nombre,edad,emg1,emg2,emg3,labels\nAda,30,0.1,0.2,0.3,rest\n"


class FakeOrderRepository:
    def __init__(self, order):
        self.order = order

    async def get_by_id(self, order_id: str):
        return self.order


class FakeDataFileRepository:
    def __init__(self):
        self.created = None

    async def create(self, **kwargs):
        self.created = kwargs
        return SimpleNamespace(id=kwargs["file_id"], **kwargs)


def _upload(content: bytes, filename: str = "session.csv") -> UploadFile:
    return UploadFile(file=BytesIO(content), filename=filename)


@pytest.fixture
def use_case_factory(tmp_path):
    def factory(**kwargs):
        order = SimpleNamespace(id="order-1", device_id="device-1")
        datafiles = FakeDataFileRepository()
        use_case = UploadCSV(
            FakeOrderRepository(order),
            datafiles,
            storage_base_path=str(tmp_path / "data"),
            **kwargs,
        )
        return use_case, datafiles

    return factory


@pytest.mark.asyncio
async def test_upload_stores_file_with_sha256_checksum(use_case_factory, tmp_path):
    use_case, datafiles = use_case_factory()

    data_file = await use_case.execute("order-1", _upload(VALID_CSV))

    assert data_file.checksum == hashlib.sha256(VALID_CSV).hexdigest()
    stored = tmp_path / "data"
    written = list(stored.glob("*.csv"))
    assert len(written) == 1
    assert written[0].read_bytes() == VALID_CSV
    assert list(stored.iterdir()) == written  # no temp leftovers


@pytest.mark.asyncio
async def test_upload_rejects_non_csv_extension(use_case_factory, tmp_path):
    use_case, _ = use_case_factory()

    with pytest.raises(ValueError):
        await use_case.execute("order-1", _upload(VALID_CSV, filename="payload.exe"))

    assert list((tmp_path / "data").iterdir()) == []


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(use_case_factory, tmp_path):
    use_case, _ = use_case_factory(max_size_bytes=32)
    oversized = b"a,b\n" + b"1,2\n" * 100

    with pytest.raises(ValueError):
        await use_case.execute("order-1", _upload(oversized))

    assert list((tmp_path / "data").iterdir()) == []


@pytest.mark.asyncio
async def test_upload_rejects_binary_payload_named_csv(use_case_factory, tmp_path):
    use_case, _ = use_case_factory()

    with pytest.raises(ValueError):
        await use_case.execute("order-1", _upload(b"\x00\x01\x02binary"))

    assert list((tmp_path / "data").iterdir()) == []


@pytest.mark.asyncio
async def test_upload_rejects_empty_file(use_case_factory, tmp_path):
    use_case, _ = use_case_factory()

    with pytest.raises(ValueError):
        await use_case.execute("order-1", _upload(b""))

    assert list((tmp_path / "data").iterdir()) == []
