import csv
import hashlib
import io
import os
import tempfile
import uuid

from fastapi import UploadFile

from app.repositories.datafile_repository import DataFileRepository
from app.repositories.order_repository import OrderRepository

DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
HEADER_SAMPLE_BYTES = 64 * 1024


class UploadCSV:
    def __init__(
        self,
        order_repository: OrderRepository,
        datafile_repository: DataFileRepository,
        storage_base_path: str = "storage/data",
        max_size_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
    ):
        self.order_repository = order_repository
        self.datafile_repository = datafile_repository
        self.storage_base_path = storage_base_path
        self.max_size_bytes = max_size_bytes

        # Ensure storage directory exists
        os.makedirs(self.storage_base_path, exist_ok=True)

    async def execute(self, order_id: str, file: UploadFile):
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        self._validate_filename(file.filename)

        file_id = str(uuid.uuid4())
        filename = f"{order_id}_{file_id}.csv"
        file_path = os.path.join(self.storage_base_path, filename)

        # Write to a temporary file first so a rejected upload never leaves a
        # partial or unvalidated file in the storage directory.
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=self.storage_base_path, prefix=".upload-", suffix=".part"
        )
        digest = hashlib.sha256()
        size_bytes = 0
        header_sample = b""

        try:
            with os.fdopen(tmp_fd, "wb") as buffer:
                while chunk := await file.read(CHUNK_SIZE):
                    size_bytes += len(chunk)
                    if size_bytes > self.max_size_bytes:
                        raise ValueError(
                            f"CSV file exceeds the maximum allowed size of "
                            f"{self.max_size_bytes} bytes"
                        )
                    if b"\x00" in chunk:
                        raise ValueError("CSV file contains binary data")
                    if len(header_sample) < HEADER_SAMPLE_BYTES:
                        header_sample += chunk[:HEADER_SAMPLE_BYTES]
                    buffer.write(chunk)
                    digest.update(chunk)

            self._validate_content(size_bytes, header_sample)
            os.replace(tmp_path, file_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

        data_file = await self.datafile_repository.create(
            file_id=file_id,
            order_id=order_id,
            device_id=order.device_id,
            storage_path=file_path,
            file_size=size_bytes,
            checksum=digest.hexdigest(),
        )

        return data_file

    @staticmethod
    def _validate_filename(filename: str | None) -> None:
        if not filename or not filename.lower().endswith(".csv"):
            raise ValueError("Only .csv files are accepted")

    @staticmethod
    def _validate_content(size_bytes: int, header_sample: bytes) -> None:
        if size_bytes == 0:
            raise ValueError("CSV file is empty")

        try:
            text = header_sample.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("CSV file must be UTF-8 encoded text") from exc

        header_line = text.splitlines()[0] if text.splitlines() else ""
        header = next(csv.reader(io.StringIO(header_line)), [])
        if not header or not any(column.strip() for column in header):
            raise ValueError("CSV file has no readable header row")
