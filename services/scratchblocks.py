"""
Scratchblocks rendering service.
"""

import os

from pyppeteer import launch

TEMPLATE_PATH = "scratchblocks_template.html"
TEMP_HTML = "private/temp_scratchblocks.html"
CHROMIUM_PATH = "/usr/bin/chromium-browser"


async def render_blocks_image(
    code: str,
    style: str,
    output_path: str = "private/blocks.png",
) -> str:
    """
    Render scratchblocks code to a PNG image.

    :param code:        Scratchblocks source code.
    :param style:       Rendering style (``scratch3``, ``scratch3-high-contrast``, ``scratch2``).
    :param output_path: Destination path for the rendered image.
    :return: The *output_path*.
    """
    with open(TEMPLATE_PATH, encoding="utf-8") as fh:
        html = fh.read()

    # Inject user code (escape HTML entities first)
    safe_code = code.replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "\n")
    html = html.replace("when green flag clicked\nsay [Hello world!]", safe_code)

    # Apply chosen style
    html = html.replace('style: "scratch3"', f'style: "{style}"')

    # Rewrite scratchblocks asset paths
    html = html.replace(
        "scratchblocks/build/scratchblocks.min.js",
        "../private/scratchblocks/build/scratchblocks.min.js",
    )
    html = html.replace(
        "scratchblocks/build/translations-all.js",
        "../private/scratchblocks/build/translations-all.js",
    )

    with open(TEMP_HTML, "w", encoding="utf-8") as fh:
        fh.write(html)

    browser = await launch(
        executablePath=CHROMIUM_PATH, headless=True, args=["--no-sandbox"]
    )
    page = await browser.newPage()

    await page.setViewport({"width": 800, "height": 600, "deviceScaleFactor": 2})
    await page.goto(f"file://{os.path.abspath(TEMP_HTML)}")

    await page.waitForFunction("typeof scratchblocks !== 'undefined'")
    await page.waitForSelector(".scratchblocks")

    element = await page.querySelector(".preview")
    await element.screenshot({"path": output_path, "omitBackground": True})
    await browser.close()

    return output_path
