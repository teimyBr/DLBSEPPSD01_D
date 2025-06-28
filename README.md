# Bucket service

This service provides REST endpoints for updating data (e.g. images) to the bucket and downloading presigned URLs using basic auth.

## Service endpoints

* Upload (REST endpoint to upload files)
* Get presigned url (REST endpoint to receive presigned URL)
* Swagger UI endpoint documentation and REST endpoints

## Basic auth access

To use the REST endpoints, basic auth credentials (user and password) are needed.

## Using Swagger UI

Acess after starting docker compose.

```
http://localhost:8000/docs 
```

## Upload files

The REST endpoint can handle the following form data for uploads:

* prefix (optional): file prefix (e.g. `folder1/folder2/`)
* file (required): file to upload (e.g.: `picture.jpg`)

The `prefix` can be used to specify folders to store the uploaded file on
the Bucket. E.g. `folder1/folder2/picture.jpg` on the example above.

### Using Swagger UI

Open the Swagger UI and use the `Try it out` feature to upload a file.

## Download files

Download a previously uploaded file by its filename or by its path (prefix + filename)

## Get presigned URL

The REST endpoint can handle the following form data to receive a presigned URL:

* filename (required): file to download via presigned URL (e.g.: `picture.jpg`)
* expiration_hours (optional): URL valid time in hours (default: 7 days)

The `filename` can also be a path, e.g. `folder/picture.jpg`.

**Hint**
Incorrect filenames will still result in valid presigned URLs. On access a
`NoSuchKey` code will be shown.

### Return
```json
{
  "status":"URL retrieved successfully",
  "url":"https://new-presiged-url",
  "expiration_hours":168
}
```

## Development

### docker compose

Start bucket-service and minio instance via docker compose

```bash
docker compose up
```

Append --build to rebuild the image with local changes

```bash
docker compose up --build
```

Default auth credentials are taken from /secrets/test file. Additional credentials can be added as separate files to 
the secrets folder.

### Prepare venv environment

```bash
./prepare.sh
```

### Update requirements

Add new dependencies to `./dev_requirements.txt` and run:

```bash
./prepare.sh
```

### Prepare test venv environment

```bash
./prepare_test.sh
```

### Update test requirements

Add new dependencies to `./dev_test_requirements.txt` and run:

```bash
./prepare_test.sh
```

### Run tests

```bash
./run_tests.sh
```
