// Simple Word Processor - Main Application Logic

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const editor = document.getElementById('editor');
    const charCount = document.getElementById('charCount');
    const wordCount = document.getElementById('wordCount');
    
    // Toolbar buttons
    const boldBtn = document.getElementById('boldBtn');
    const italicBtn = document.getElementById('italicBtn');
    const underlineBtn = document.getElementById('underlineBtn');
    const strikeBtn = document.getElementById('strikeBtn');
    
    const fontFamily = document.getElementById('fontFamily');
    const fontSize = document.getElementById('fontSize');
    const headingStyle = document.getElementById('headingStyle');
    
    const alignLeftBtn = document.getElementById('alignLeftBtn');
    const alignCenterBtn = document.getElementById('alignCenterBtn');
    const alignRightBtn = document.getElementById('alignRightBtn');
    const alignJustifyBtn = document.getElementById('alignJustifyBtn');
    
    const bulletListBtn = document.getElementById('bulletListBtn');
    const numberListBtn = document.getElementById('numberListBtn');
    
    const textColorBtn = document.getElementById('textColorBtn');
    const bgColorBtn = document.getElementById('bgColorBtn');
    
    const undoBtn = document.getElementById('undoBtn');
    const redoBtn = document.getElementById('redoBtn');
    const clearBtn = document.getElementById('clearBtn');
    
    const screenshotBtn = document.getElementById('screenshotBtn');
    const screenshotStatus = document.getElementById('screenshotStatus');

    // Initialize editor
    editor.focus();
    updateStatusBar();

    // Formatting functions
    function execCommand(command, value = null) {
        document.execCommand(command, false, value);
        editor.focus();
        updateButtonStates();
    }

    function formatBlock(tag) {
        document.execCommand('formatBlock', false, tag);
        editor.focus();
        updateButtonStates();
    }

    // Update button active states based on current selection
    function updateButtonStates() {
        boldBtn.classList.toggle('active', document.queryCommandState('bold'));
        italicBtn.classList.toggle('active', document.queryCommandState('italic'));
        underlineBtn.classList.toggle('active', document.queryCommandState('underline'));
        strikeBtn.classList.toggle('active', document.queryCommandState('strikeThrough'));
    }

    // Update character and word count
    function updateStatusBar() {
        const text = editor.innerText.trim();
        const chars = text.length;
        const words = text.length > 0 ? text.split(/\s+/).filter(word => word.length > 0).length : 0;
        
        charCount.textContent = `${chars} character${chars !== 1 ? 's' : ''}`;
        wordCount.textContent = `${words} word${words !== 1 ? 's' : ''}`;
    }

    // Event Listeners - Formatting
    boldBtn.addEventListener('click', () => execCommand('bold'));
    italicBtn.addEventListener('click', () => execCommand('italic'));
    underlineBtn.addEventListener('click', () => execCommand('underline'));
    strikeBtn.addEventListener('click', () => execCommand('strikeThrough'));

    fontFamily.addEventListener('change', (e) => execCommand('fontName', e.target.value));
    fontSize.addEventListener('change', (e) => execCommand('fontSize', '7') || execCommand('fontSize', e.target.value + 'px'));
    
    // Custom font size handler (execCommand fontSize is inconsistent)
    fontSize.addEventListener('change', function(e) {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const span = document.createElement('span');
            span.style.fontSize = e.target.value + 'px';
            
            try {
                range.surroundContents(span);
            } catch (ex) {
                // If surroundContents fails, use execCommand fallback
                execCommand('fontSize', '7');
                const fontElements = editor.querySelectorAll('font[size="7"]');
                fontElements.forEach(el => {
                    el.removeAttribute('size');
                    el.style.fontSize = e.target.value + 'px';
                });
            }
        }
        editor.focus();
    });

    headingStyle.addEventListener('change', (e) => formatBlock(e.target.value));

    // Alignment
    alignLeftBtn.addEventListener('click', () => execCommand('justifyLeft'));
    alignCenterBtn.addEventListener('click', () => execCommand('justifyCenter'));
    alignRightBtn.addEventListener('click', () => execCommand('justifyRight'));
    alignJustifyBtn.addEventListener('click', () => execCommand('justifyFull'));

    // Lists
    bulletListBtn.addEventListener('click', () => execCommand('insertUnorderedList'));
    numberListBtn.addEventListener('click', () => execCommand('insertOrderedList'));

    // Colors
    textColorBtn.addEventListener('change', (e) => execCommand('foreColor', e.target.value));
    bgColorBtn.addEventListener('change', (e) => execCommand('hiliteColor', e.target.value));

    // Undo/Redo
    undoBtn.addEventListener('click', () => execCommand('undo'));
    redoBtn.addEventListener('click', () => execCommand('redo'));

    // Clear all
    clearBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all content?')) {
            editor.innerHTML = '<p><br></p>';
            editor.focus();
            updateStatusBar();
        }
    });

    // Editor events
    editor.addEventListener('input', updateStatusBar);
    editor.addEventListener('keyup', updateButtonStates);
    editor.addEventListener('mouseup', updateButtonStates);

    // Keyboard shortcuts
    editor.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key.toLowerCase()) {
                case 'b':
                    e.preventDefault();
                    execCommand('bold');
                    break;
                case 'i':
                    e.preventDefault();
                    execCommand('italic');
                    break;
                case 'u':
                    e.preventDefault();
                    execCommand('underline');
                    break;
                case 'z':
                    if (!e.shiftKey) {
                        e.preventDefault();
                        execCommand('undo');
                    }
                    break;
                case 'y':
                    e.preventDefault();
                    execCommand('redo');
                    break;
            }
        }
    });

    // Screenshot functionality
    screenshotBtn.addEventListener('click', async function() {
        try {
            screenshotStatus.textContent = 'Capturing screenshot...';
            screenshotBtn.disabled = true;

            const viewportContainer = document.getElementById('viewport-container');
            
            // Use html2canvas to capture the viewport
            const canvas = await html2canvas(viewportContainer, {
                width: 1280,
                height: 720,
                scale: 2, // Higher quality
                backgroundColor: '#ffffff',
                logging: false
            });

            // Convert canvas to blob and download
            canvas.toBlob(function(blob) {
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
                link.download = `word-processor-screenshot-${timestamp}.png`;
                link.href = url;
                link.click();
                
                // Cleanup
                URL.revokeObjectURL(url);
                
                screenshotStatus.textContent = 'Screenshot saved!';
                screenshotBtn.disabled = false;
                
                setTimeout(() => {
                    screenshotStatus.textContent = '';
                }, 3000);
            }, 'image/png');

        } catch (error) {
            console.error('Screenshot failed:', error);
            screenshotStatus.textContent = 'Screenshot failed!';
            screenshotBtn.disabled = false;
            
            setTimeout(() => {
                screenshotStatus.textContent = '';
            }, 3000);
        }
    });

    // Prevent drag and drop of images/files (keep it simple)
    editor.addEventListener('drop', function(e) {
        e.preventDefault();
    });

    editor.addEventListener('dragover', function(e) {
        e.preventDefault();
    });

    // Initialize button states
    updateButtonStates();
});

