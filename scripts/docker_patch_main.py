"""
Patches main.py at Docker build time to serve the built frontend as static files.
Called in the Dockerfile after the frontend is built and copied into the image.
"""
import os
import re


def main():
    main_py = os.path.join(os.path.dirname(__file__), "..", "backend", "main.py")
    main_py = os.path.abspath(main_py)
    static_dir = os.path.join(os.path.dirname(main_py), "static")

    if not os.path.isdir(static_dir):
        print(f"static dir not found ({static_dir}) — skipping frontend mount")
        return

    if not os.listdir(static_dir):
        print(f"static dir is empty ({static_dir}) — skipping frontend mount")
        return

    with open(main_py, "r") as f:
        content = f.read()

    # Guard: don't patch twice
    if "# [Docker] Serve built frontend" in content:
        print("main.py already patched — skipping")
        return

    insert_block = '''


# [Docker] Serve built frontend as static files
import os as _os
import fastapi.staticfiles as _sf
_static = _os.path.join(_os.path.dirname(__file__), "static")
if _os.path.isdir(_static) and _os.listdir(_static):
    app.mount("/", _sf.StaticFiles(directory=_static, html=True), name="frontend")
'''

    # Insert before the __name__ == "__main__" guard
    content = content.replace(
        'if __name__ == "__main__":',
        insert_block + '\n' + 'if __name__ == "__main__":'
    )

    with open(main_py, "w") as f:
        f.write(content)

    print("main.py patched with frontend static serving ✓")


if __name__ == "__main__":
    main()
