# CT Scan Annotation Feature Guide

## Overview

The CT scan annotation feature allows users to add visual annotations to CT scan images before using them in conversations. This includes drawing tools, text annotations, and shape markers to highlight important areas in medical images.

## Features

### Available Tools

1. **Pen Tool** ✏️
   - Freehand drawing
   - Perfect for highlighting specific areas or drawing attention to details

2. **Rectangle Tool** ⬜
   - Draw rectangular boxes
   - Useful for marking regions of interest

3. **Circle Tool** ⭕
   - Draw circular markers
   - Great for pinpointing specific locations

4. **Text Tool** T
   - Add text labels
   - Click where you want text, then type your annotation

5. **Arrow Tool** ➡️
   - Draw arrows pointing to specific areas
   - Useful for indicating direction or pointing to features

### Color Options

- 8 different colors available: Red, Green, Blue, Yellow, Magenta, Cyan, White, Black
- Choose colors that provide good contrast against the CT scan image

### Line Width Control

- Adjustable line width from 1px to 10px
- Use thicker lines for better visibility on medical images

## How to Use

### In CTViewer Component

1. **Load a CT scan file** - The system will automatically convert it to images
2. **Navigate through slices** - Use the slider to view different slices
3. **Click "✏️ Annotate Image"** - Opens the annotation tool
4. **Select your tool** - Choose from pen, rectangle, circle, text, or arrow
5. **Choose color and line width** - Adjust as needed
6. **Draw on the image** - Click and drag to create annotations
7. **Add text** - Click the text tool, then click where you want text and type
8. **Save your annotation** - Click "Save Annotation" when done
9. **Use the slice** - The annotated image will be included when you submit

### In CTScanPopup Component

1. **Upload CT files** - Select both .mhd and .raw files
2. **View converted slices** - All slices will be displayed in a grid
3. **Click the ✏️ button** on any slice to annotate it
4. **Use annotation tools** - Same tools available as in CTViewer
5. **Save annotation** - Your changes are automatically saved
6. **Select slices** - Choose which annotated slices to use
7. **Confirm selection** - Annotated images will be included in your selection

## Annotation Workflow

### Step-by-Step Process

1. **Prepare your CT scan files**
   - Ensure you have both .mhd and .raw files
   - Files should be properly paired

2. **Convert to images**
   - The system automatically converts CT files to viewable images
   - Wait for conversion to complete

3. **Review slices**
   - Navigate through different slices
   - Identify areas that need annotation

4. **Add annotations**
   - Use appropriate tools for your needs
   - Consider using different colors for different types of annotations
   - Add text labels for clarity

5. **Save and use**
   - Save your annotations
   - The annotated images will be included in your conversation

## Best Practices

### Medical Annotation Guidelines

1. **Use clear, contrasting colors**
   - Red and green work well for highlighting
   - Avoid colors that blend with the image

2. **Keep annotations minimal**
   - Don't overcrowd the image
   - Focus on the most important areas

3. **Use text sparingly**
   - Keep text labels short and clear
   - Position text where it doesn't obscure important details

4. **Be consistent**
   - Use the same colors for similar types of annotations
   - Maintain consistent line widths

### Technical Tips

1. **Save frequently**
   - Click "Save Annotation" after making significant changes
   - This prevents loss of work

2. **Use undo when needed**
   - The "Undo Last" button removes the most recent annotation
   - Use "Clear All" to start over completely

3. **Test visibility**
   - Ensure annotations are clearly visible
   - Adjust line width and color as needed

## Troubleshooting

### Common Issues

1. **Image not loading**
   - Check that both .mhd and .raw files are present
   - Ensure files are properly paired
   - Try refreshing the page

2. **Annotations not saving**
   - Make sure you click "Save Annotation"
   - Check that you have at least one annotation
   - Verify the image loaded properly

3. **Tool not working**
   - Ensure you've selected the correct tool
   - Check that the canvas is properly loaded
   - Try refreshing the annotation tool

4. **Text not appearing**
   - Make sure you clicked the text tool first
   - Click on the image where you want text
   - Type your text and press Enter or click Add

## Integration

The annotation feature integrates seamlessly with the existing chat system:

- Annotated images are automatically included when you submit slices
- The original image data is preserved
- Annotations are saved as part of the image data
- No additional setup required

## Future Enhancements

Potential improvements for the annotation system:

1. **Measurement tools** - Add rulers and measurement capabilities
2. **Layer management** - Organize annotations in layers
3. **Export options** - Save annotations separately
4. **Collaborative annotations** - Share annotations between users
5. **AI-assisted annotation** - Automatic detection of regions of interest

## Support

If you encounter issues with the annotation feature:

1. Check the browser console for error messages
2. Ensure your CT files are in the correct format
3. Try using a different browser
4. Contact support with specific error details 