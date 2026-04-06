"""Download the latest versions of JavaScript libraries for the MapLibre server.

Downloads pre-built browser bundles for:
- MapLibre GL JS (map rendering)
- Turf.js (geospatial analysis)
- MapBox GL Draw (drawing tools)

Usage:
    python update_js_libs.py

The script downloads to the js/ and css/ directories alongside this file.
After downloading, update the <script> tags in index.html and
maplibre_compare.html to reference the new filenames.
"""

import json
import os
import re
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

JS_DIR = os.path.join(SCRIPT_DIR, "js")
CSS_DIR = os.path.join(SCRIPT_DIR, "css")

JS_DIR = r"c:\work\projects\delftdashboard\dev_claude\maplibre\server\js"
CSS_DIR = r"c:\work\projects\delftdashboard\dev_claude\maplibre\server\css"


def download(url, dest):
    """Download a URL to a local file."""
    print(f"  Downloading {url}")
    print(f"  -> {os.path.basename(dest)}")
    urllib.request.urlretrieve(url, dest)
    size_kb = os.path.getsize(dest) / 1024
    print(f"  ({size_kb:.0f} KB)")


def get_latest_github_release(owner, repo):
    """Get the latest release tag from GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "Python"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["tag_name"]


def get_latest_npm_version(package):
    """Get the latest version of an npm package."""
    url = f"https://registry.npmjs.org/{package}/latest"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    return data["version"]


def update_maplibre():
    """Download the latest MapLibre GL JS."""
    print("\n=== MapLibre GL JS ===")
    version = get_latest_npm_version("maplibre-gl")
    print(f"Latest version: {version}")

    # JS bundle
    js_url = f"https://unpkg.com/maplibre-gl@{version}/dist/maplibre-gl.js"
    js_dest = os.path.join(JS_DIR, f"maplibre-gl-{version}.js")
    download(js_url, js_dest)

    # CSS
    css_url = f"https://unpkg.com/maplibre-gl@{version}/dist/maplibre-gl.css"
    css_dest = os.path.join(CSS_DIR, f"maplibre-gl-{version}.css")
    download(css_url, css_dest)

    return version


def update_turf():
    """Download the latest Turf.js."""
    print("\n=== Turf.js ===")
    version = get_latest_npm_version("@turf/turf")
    print(f"Latest version: {version}")

    js_url = f"https://unpkg.com/@turf/turf@{version}/turf.min.js"
    js_dest = os.path.join(JS_DIR, f"turf-v{version.split('.')[0]}.js")
    download(js_url, js_dest)

    return version


def update_mapbox_draw():
    """Download the latest MapBox GL Draw (original Mapbox version)."""
    print("\n=== MapBox GL Draw (original) ===")
    version = get_latest_npm_version("@mapbox/mapbox-gl-draw")
    print(f"Latest version: {version}")

    js_url = (
        f"https://unpkg.com/@mapbox/mapbox-gl-draw@{version}/dist/mapbox-gl-draw.js"
    )
    js_dest = os.path.join(JS_DIR, f"mapbox-gl-draw-v{version}.js")
    download(js_url, js_dest)

    css_url = (
        f"https://unpkg.com/@mapbox/mapbox-gl-draw@{version}/dist/mapbox-gl-draw.css"
    )
    css_dest = os.path.join(CSS_DIR, "mapbox-gl-draw.css")
    download(css_url, css_dest)

    return version


def update_maplibre_draw():
    """Download the latest maplibre-gl-draw (MapLibre-native fork)."""
    print("\n=== MapLibre GL Draw (MapLibre fork) ===")
    version = get_latest_npm_version("maplibre-gl-draw")
    print(f"Latest version: {version}")

    js_url = f"https://unpkg.com/maplibre-gl-draw@{version}/dist/mapbox-gl-draw.js"
    js_dest = os.path.join(JS_DIR, f"maplibre-gl-draw-v{version}.js")
    download(js_url, js_dest)

    css_url = f"https://unpkg.com/maplibre-gl-draw@{version}/dist/mapbox-gl-draw.css"
    css_dest = os.path.join(CSS_DIR, "maplibre-gl-draw.css")
    download(css_url, css_dest)

    return version


def update_html_references(maplibre_version, turf_version, draw_version):
    """Update script/link tags in HTML files to reference the new versions."""
    html_files = [
        os.path.join(SCRIPT_DIR, "index.html"),
        os.path.join(SCRIPT_DIR, "index_stand_alone.html"),
        os.path.join(SCRIPT_DIR, "maplibre_compare.html"),
    ]

    turf_major = turf_version.split(".")[0]

    for html_file in html_files:
        if not os.path.exists(html_file):
            continue
        with open(html_file, "r") as f:
            content = f.read()

        original = content

        # Update MapLibre JS version
        content = re.sub(
            r"maplibre-gl-[\d.]+\.js",
            f"maplibre-gl-{maplibre_version}.js",
            content,
        )
        # Update MapLibre CSS version
        content = re.sub(
            r"maplibre-gl-[\d.]+\.css",
            f"maplibre-gl-{maplibre_version}.css",
            content,
        )
        # Update MapBox Draw version
        content = re.sub(
            r"mapbox-gl-draw-v[\d.]+\.js",
            f"mapbox-gl-draw-v{draw_version}.js",
            content,
        )
        # Update Turf version
        content = re.sub(
            r"turf-v\d+\.js",
            f"turf-v{turf_major}.js",
            content,
        )

        if content != original:
            with open(html_file, "w") as f:
                f.write(content)
            print(f"  Updated {os.path.basename(html_file)}")
        else:
            print(f"  No changes in {os.path.basename(html_file)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Update JS libraries for Guitares MapLibre server"
    )
    parser.add_argument(
        "--draw",
        choices=["mapbox", "maplibre", "both"],
        default="both",
        help="Which draw library to download: mapbox (original), maplibre (fork), or both (default)",
    )
    args = parser.parse_args()

    print("Updating JavaScript libraries for Guitares MapLibre server")
    print(f"JS directory: {JS_DIR}")
    print(f"CSS directory: {CSS_DIR}")

    maplibre_ver = update_maplibre()
    turf_ver = update_turf()

    draw_ver = None
    maplibre_draw_ver = None
    if args.draw in ("mapbox", "both"):
        draw_ver = update_mapbox_draw()
    if args.draw in ("maplibre", "both"):
        maplibre_draw_ver = update_maplibre_draw()

    # Update HTML refs using whichever draw lib was downloaded
    # Default: use mapbox draw refs (maplibre-gl-draw uses the same filename pattern)
    html_draw_ver = draw_ver or maplibre_draw_ver
    print("\n=== Updating HTML references ===")
    update_html_references(maplibre_ver, turf_ver, html_draw_ver)

    print("\n=== Summary ===")
    print(f"MapLibre GL JS: {maplibre_ver}")
    print(f"Turf.js: {turf_ver}")
    if draw_ver:
        print(f"MapBox GL Draw (original): {draw_ver}")
    if maplibre_draw_ver:
        print(f"MapLibre GL Draw (fork): {maplibre_draw_ver}")
    print()
    print("To switch between draw libraries, update the <script> tag in index.html:")
    if draw_ver:
        print(f'  Mapbox:   <script src="/js/mapbox-gl-draw-v{draw_ver}.js"></script>')
    if maplibre_draw_ver:
        print(
            f'  MapLibre: <script src="/js/maplibre-gl-draw-v{maplibre_draw_ver}.js"></script>'
        )
    print()
    print("NOTE: maplibre-gl-compare.js and mapbox_gl_draw_scale_rotate_mode.js")
    print("are custom source files — NOT updated by this script.")
    print()
    print("Delete old version files after verifying everything works.")
