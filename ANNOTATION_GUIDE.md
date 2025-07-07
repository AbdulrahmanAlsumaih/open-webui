# Image Annotation Feature Guide

## Overview

The image annotation feature allows you to draw on and annotate images directly in the chat interface. This is useful for highlighting important areas, adding notes, or marking up images before sending them in a message.

## How to Use

### 1. Upload an Image
- Drag and drop an image into the chat input area, or
- Click the file upload button and select an image file

### 2. Annotate the Image
- Hover over the image in the chat input area
- Click the blue annotation button (pencil icon) that appears in the top-right corner
- The annotation modal will open with your image

### 3. Use Annotation Tools
The annotation interface provides several tools:

#### Drawing Tools:
- **Pen Tool** ✏️: Freehand drawing
- **Rectangle Tool** ⬜: Draw rectangles
- **Circle Tool** ⭕: Draw circles
- **Arrow Tool** ➡️: Draw arrows
- **Text Tool** T: Add text annotations

#### Customization:
- **Colors**: Choose from 8 different colors
- **Line Width**: Adjust the thickness of lines (1-10px)

#### Actions:
- **Clear All**: Remove all annotations
- **Undo Last**: Remove the most recent annotation
- **Save Annotation**: Apply annotations and close the modal

### 4. Save and Send
- Click "Save Annotation" to apply your changes
- The annotated image will replace the original in your message
- Send the message as usual

## Features

### Real-time Preview
- See your annotations as you draw them
- All changes are applied in real-time

### Multiple Annotation Types
- Draw freehand lines and shapes
- Add text labels
- Create arrows to point to specific areas
- Use different colors for organization

### Non-destructive Editing
- Original image is preserved
- You can always re-annotate if needed
- Annotations are applied as overlays

## Use Cases

### Educational Content
- Highlight important parts of diagrams
- Add explanatory text to images
- Mark up screenshots for tutorials

### Medical Imaging
- Annotate CT scans or X-rays
- Mark areas of interest
- Add measurements or notes

### Design Feedback
- Mark up design mockups
- Point out specific elements
- Add comments to screenshots

### Technical Documentation
- Highlight UI elements
- Mark bugs or issues
- Add explanatory arrows

## Tips

1. **Use different colors** to organize different types of annotations
2. **Adjust line width** for better visibility on different image sizes
3. **Use text annotations** for detailed explanations
4. **Combine tools** for comprehensive annotations
5. **Save frequently** to avoid losing work

## Keyboard Shortcuts

- **Escape**: Close the annotation modal
- **Enter** (in text mode): Add text annotation
- **Mouse drag**: Draw shapes and lines
- **Click**: Place text or start drawing

## Technical Notes

- Supported image formats: PNG, JPG, JPEG, GIF, WebP, AVIF
- Annotations are saved as base64-encoded PNG images
- The original image quality is preserved
- All annotations are applied client-side for privacy 