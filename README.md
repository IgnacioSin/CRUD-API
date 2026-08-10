# Task API

**CRUD API for managing tasks, using in-memory storage.** This was made as a part of an assignment for FlyRank's professional internship.

*The list of tasks comes with three initial tasks*

## Requirements

Python 3.10+

## Installation & running

```bash
git clone https://github.com/IgnacioSin/CRUD-API.git
cd CRUD-API
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Git Bash)
source .venv/Scripts/activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
python -m uvicorn main:app --reload
```

Alternatively, using the FastAPI CLI:

```bash
fastapi dev main.py
```

The API runs at `http://localhost:8000`.

## Endpoints

| Endpoint | Description | Success | Errors |
|--------|-------------|---------|--------|
|`GET /`|Returns basic information about the API|`200`||
|`GET /health`|Returns the health status of the API|`200`||
|`GET /tasks`|Returns a list of all tasks|`200`||
|`POST /tasks`|Creates a new task with the provided title|`201`|`400`|
|`GET /tasks/{id}`|Returns a single task by its ID|`200`|`404`|
|`PUT /tasks/{id}`|Updates a task with the provided ID|`200`|`400` or `404`|
|`DELETE /tasks/{id}`|Deletes a task with the provided ID|`204`|`404`|

## Example request

**Input:**

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"New Task"}'
```

**Output:**

```http
HTTP/1.1 201 Created
date: Mon, 10 Aug 2026 09:55:34 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"New Task","done":false}
```

## Interactive documentation

Interactive docs at `http://localhost:8000/docs`

![Swagger UI](docs/swagger.png)

## Known limitations

Tasks are stored in a Python list in the server's memory, so all data is lost
when the process stops. The `next_id` counter resets as well, which means IDs
can be reissued to different tasks after a restart.

Validation errors raised by FastAPI itself (for example, a non-integer ID)
return a `422` with a `detail` field, while the API's own errors return `400`
or `404` with an `error` field.

## AI vs me

After building this API by hand (Stages 0–6), I asked an AI assistant to build
the same thing from a prompt written from memory, then compared the results.

### My prompt

> I need a ai_main.py file of a CRUD API for maganing tasks. It should use fast
> api and have just in-memory data. I want it to do the functions of GET, POST,
> PUT and DELETE.

The AI's version is in [`ai-version/`](ai-version/).

### What the AI did better

**Used a dictionary keyed by ID instead of a list.** [Explain: your version
loops over every task to find one; a dict looks it up directly. Why that
matters as the collection grows.]

**Handled partial updates with `model_dump(exclude_unset=True)` and
`model_copy(update=...)`.** [Explain: this returns only the fields the client
actually sent, so omitted fields are left untouched automatically. Compare to
your per-field `is not None` checks — and note this took you six revisions.]

### What it got wrong or ignored

| Behavior | My version | AI version |
|---|---|---|
| Fresh `GET /tasks` | 3 seed tasks | `[]` |
| `POST {}` | `400` + `{"error": ...}` | `422` + `{"detail": [...]}` |
| Task schema | `id`, `title`, `done` | `id`, `title`, `description`, `completed` |
| `GET /` | `200` | `404` — not implemented |
| `GET /health` | `200` | `404` — not implemented |
| `GET /tasks/99` | `404` + `{"error": ...}` | `404` + `{"detail": ...}` |

It also produced a file named `ai_main.py`, which Python cannot import —
module names can't contain hyphens. [One sentence: it followed your filename
instruction exactly, into a file that doesn't run.]

### What my prompt forgot to specify

[Write this yourself — it's the actual conclusion. Cover: you named the four
methods but no status codes; no schema; no seed data; only five of your seven
endpoints; no error body shape; no validation rule. Then the point: every
difference in the table above traces to a gap in the prompt, not to the AI
being wrong. It got 201, 204 and 404 right without being told, because those
are strong conventions — everything unconventional it invented, reasonably.]