# Data governance for EMGTRAINNER

EMGTRAINNER records EMG samples, participant/session labels, exported CSVs, and derived model artifacts. Treat everything under `backend/storage/` as private runtime data unless a maintainer has explicitly prepared an anonymized fixture for publication.

## Policy

- Do not commit real session exports, participant folders, label aggregates, trained models, or ad-hoc analysis files from `backend/storage/`.
- Keep private data on the operator machine, in approved private object storage, or in a separately controlled backup location.
- Use only synthetic, anonymized, or consent-cleared fixtures for tests and demos, and store those outside `backend/storage/` with documentation explaining their source.
- Do not rewrite Git history as part of routine quarantine work. History cleanup is a separate, explicit operation that requires coordination because it changes repository ancestry for every collaborator.

## Local storage workflow

1. Run the backend normally; it may create private runtime data under `backend/storage/`.
2. Before sharing code, verify that future storage files are ignored:
   ```bash
   git check-ignore -v backend/storage/sessions/example.csv
   git check-ignore -v backend/storage/by_label/Abrir.csv
   git check-ignore -v backend/storage/models/model.bin
   ```
3. Review pending changes with `git status --short`. Real data under `backend/storage/` should not appear as new files.
4. If a storage file is already tracked, remove it from Git with a normal deletion or `git rm` in a dedicated data-quarantine change. Do not commit replacement real data.

## Backups and recovery

- Keep backups outside the repository. For the current quarantine, a pre-change backup was delivered separately at `/home/hombrenaranja/Downloads/emgtrainner-backend-storage-20260808_215716.zip` with SHA-256 `47dc59f3a709c4bd46f4bfdba524946e795b506a21590a24005078eabeef2c53`.
- To recover quarantined data locally, restore from an approved private backup into `backend/storage/`. The restored files should remain ignored by Git.
- If the team later decides to purge historical copies from Git history, perform that as a separate history-rewrite procedure after notifying collaborators and preserving private backups.

## Storage access boundary (Phase 2)

- `GET /api/v1/storage/sessions` and `GET /api/v1/storage/sessions/{filename}` require an authenticated bearer token.
- Session downloads canonicalize the requested path with `os.path.realpath` and refuse anything that resolves outside the storage root, including absolute paths, `..` segments, and escaping symlinks.
- Order CSV upload and download (`POST /orders/{order_id}/upload`, `GET /orders/{order_id}/csv`) require an authenticated bearer token.
- Uploads are bounded (25 MB by default), must use a `.csv` filename, must be non-empty UTF-8 text with a readable header row, and are written to a temporary file that is only moved into place after validation succeeds.
- Upload integrity metadata uses SHA-256. Legacy rows created before this change still hold MD5 checksums; there is no backfill.

### Remaining risk: ownership

Authentication is enforced, but authorization is not scoped per user: any authenticated caller can list and download any stored session or order CSV. A per-user/per-patient ownership model requires DB relations that do not exist yet and is deliberately out of scope for this phase.
