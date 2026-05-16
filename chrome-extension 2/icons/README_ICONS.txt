ICON GENERATION INSTRUCTIONS
============================

To generate the required PNG icons from the SVG:

1. Use any SVG to PNG converter (e.g., https://svgtopng.com)
2. Convert icon.svg to the following sizes:
   - icon16.png (16x16)
   - icon48.png (48x48)
   - icon128.png (128x128)

3. Save all PNG files in this icons/ directory

Alternative: Use ImageMagick command line:
- convert icon.svg -resize 16x16 icon16.png
- convert icon.svg -resize 48x48 icon48.png
- convert icon.svg -resize 128x128 icon128.png

The SVG icon represents:
- Robot head for AI assistance
- Contract document at bottom
- Conga brand colors (purple gradient)
- Clean, professional design suitable for office environments