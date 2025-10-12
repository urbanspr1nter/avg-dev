# Simple Word Processor

A lightweight, pure front-end word processor built for GUI agent demonstrations and testing.

## Features

- **Text Formatting**: Bold, Italic, Underline, Strikethrough
- **Font Controls**: Multiple font families and sizes
- **Heading Styles**: H1 through H4 plus Normal paragraph
- **Text Alignment**: Left, Center, Right, Justify
- **Lists**: Bullet and Numbered lists
- **Colors**: Text color and highlight/background color
- **Undo/Redo**: Full history support
- **Keyboard Shortcuts**: 
  - Ctrl/Cmd + B (Bold)
  - Ctrl/Cmd + I (Italic)
  - Ctrl/Cmd + U (Underline)
  - Ctrl/Cmd + Z (Undo)
  - Ctrl/Cmd + Y (Redo)
- **Screenshot Capture**: Button to capture the viewport as PNG

## Viewport

The editor is constrained to exactly **1280x720 pixels** for consistent screenshots and GUI agent testing.

## Usage

Simply open `index.html` in a web browser. No build process or server required!

The screenshot button is positioned outside the viewport so it won't appear in captures.

## Technical Details

- Pure HTML/CSS/JavaScript (no frameworks)
- Uses `contenteditable` for rich text editing
- `html2canvas` library for screenshot functionality
- No backend, no persistence - purely client-side

## Purpose

This application is designed as a testing ground for GUI agents, providing a realistic web application interface for demonstrations and screenshot generation.

