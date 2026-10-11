# Pages

A **page** is the content unit of a notebook: HTML that lives in a **section**.
You create one by `POST`ing a `multipart/form-data` body — the HTML as the
presentation part, plus one part per embedded image or file. The library builds
that body for you. Requires `Notes.ReadWrite` (`Notes.Read` to only read).

## Create a page from HTML

Headings, paragraphs, lists, tables and styled spans all translate into OneNote
content. The `<title>` becomes the page title.

```python
page = section.pages.add(
    presentation_file="<html><head><title>Notes</title></head><body><p>Hello</p></body></html>"
).execute_query()
print(page.title, page.links.oneNoteWebUrl.href)
```

→ [`create.py`](./create.py)

## Embed an image and attach files

The HTML points at named parts (`<img src="name:imageBlock1">`,
`<object data="name:fileBlock1">`) and a mapping supplies the bytes. Each file's
name selects the MIME type of its part.

```python
attachments = {"imageBlock1": image_file, "fileBlock1": pdf_file}
page = section.pages.add(presentation_file=html_file, attachment_files=attachments).execute_query()
```

→ [`attachments.py`](./attachments.py)

## Download a page's HTML

`get_content()` returns the rendered HTML, including the `name:` references to
embedded parts. Use it to archive or export a page. Fetch it from the top-level
page resource — the nested section path is not accepted by the content endpoint.

```python
html = client.me.onenote.pages[page.id].get_content().execute_query().value
```

→ [`read.py`](./read.py)

Both write examples clean up after themselves by deleting the page they created;
pass `--keep` to leave it in place. (Deleting a *notebook*, unlike a page, is not
supported by Graph — see the *Sharp edges* section of the [tour](../README.md).)
