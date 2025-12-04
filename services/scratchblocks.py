"""
Scratchblocks rendering service.
"""

import os
from pyppeteer import launch

TEMPLATE_PATH = "ScratchOn/scratchblocks_template.html"


async def render_blocks_image(
    code: str, style: str, output_path: str = "ScratchOn_private/blocks.png"
) -> str:
    """
    Renders scratchblocks code to an image.

    :param code: Scratchblocks code to render.
    :param style: Style to use (scratch3, scratch3-high-contrast, scratch2).
    :param output_path: Path to save the rendered image.
    :return: Path to the rendered image.
    """
    # Load the HTML template
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Inject user code
    html = html.replace(
        "when green flag clicked\nsay [Hello world!]",
        code.replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "\n"),
    )

    # Add chosen style
    html = html.replace('style: "scratch3"', f'style: "{style}"')

    # Update scratchblocks path
    html = html.replace(
        "scratchblocks/build/scratchblocks.min.js",
        "../ScratchOn/scratchblocks/build/scratchblocks.min.js",
    )
    html = html.replace(
        "scratchblocks/build/translations-all.js",
        "../ScratchOn/scratchblocks/build/translations-all.js",
    )

    # Save modified HTML to a temporary file
    temp_path = "ScratchOn_private/temp_scratchblocks.html"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Launch chromium browser using Pyppeteer
    browser = await launch(
        executablePath="/usr/bin/chromium-browser", headless=True, args=["--no-sandbox"]
    )
    page = await browser.newPage()

    await page.setViewport(
        {
            "width": 800,
            "height": 600,
            "deviceScaleFactor": 2,  # Improves output resolution
        }
    )

    # Navigate to the temporary file
    await page.goto(f"file://{os.path.abspath(temp_path)}")

    # Wait for scratchblocks to load
    await page.waitForFunction("typeof scratchblocks !== 'undefined'")
    await page.waitForSelector(".scratchblocks")

    # Screenshot the result
    element = await page.querySelector(".preview")
    await element.screenshot({"path": output_path, "omitBackground": True})
    await browser.close()

    return output_path
