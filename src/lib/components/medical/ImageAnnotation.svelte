<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import { toast } from 'svelte-sonner';

    export let imageSrc: string;
    export let imageAlt: string = 'Image';
    export let show = false;

    const dispatch = createEventDispatcher();

    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D;
    let imageElement: HTMLImageElement;
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    let selectedTool: 'pen' | 'rectangle' | 'circle' | 'text' | 'arrow' = 'pen';
    let selectedColor = '#ff0000';
    let lineWidth = 3;
    let annotations: Array<{
        type: string;
        data: any;
        color: string;
        lineWidth: number;
    }> = [];
    let currentAnnotation: any = null;
    let textInput = '';
    let showTextInput = false;
    let textPosition = { x: 0, y: 0 };

    const colors = [
        '#ff0000', '#00ff00', '#0000ff', '#ffff00', 
        '#ff00ff', '#00ffff', '#ffffff', '#000000'
    ];

    const tools: Array<{ id: 'pen' | 'rectangle' | 'circle' | 'text' | 'arrow'; name: string; icon: string }> = [
        { id: 'pen', name: 'Pen', icon: '✏️' },
        { id: 'rectangle', name: 'Rectangle', icon: '⬜' },
        { id: 'circle', name: 'Circle', icon: '⭕' },
        { id: 'text', name: 'Text', icon: 'T' },
        { id: 'arrow', name: 'Arrow', icon: '➡️' }
    ];

    onMount(() => {
        if (canvas) {
            ctx = canvas.getContext('2d')!;
            setupCanvas();
        }
    });

    function setupCanvas() {
        if (!canvas || !imageElement) return;
        
        // Set canvas size to match image
        canvas.width = imageElement.naturalWidth;
        canvas.height = imageElement.naturalHeight;
        
        // Clear canvas and redraw
        redrawCanvas();
    }

    function redrawCanvas() {
        if (!ctx || !imageElement) return;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw image
        ctx.drawImage(imageElement, 0, 0, canvas.width, canvas.height);
        
        // Redraw all annotations
        annotations.forEach(annotation => {
            drawAnnotation(annotation);
        });
    }

    function drawAnnotation(annotation: any) {
        if (!ctx) return;
        
        ctx.strokeStyle = annotation.color;
        ctx.fillStyle = annotation.color;
        ctx.lineWidth = annotation.lineWidth;
        
        switch (annotation.type) {
            case 'pen':
                if (annotation.data.points && annotation.data.points.length > 1) {
                    ctx.beginPath();
                    ctx.moveTo(annotation.data.points[0].x, annotation.data.points[0].y);
                    for (let i = 1; i < annotation.data.points.length; i++) {
                        ctx.lineTo(annotation.data.points[i].x, annotation.data.points[i].y);
                    }
                    ctx.stroke();
                }
                break;
                
            case 'rectangle':
                ctx.strokeRect(
                    annotation.data.x, 
                    annotation.data.y, 
                    annotation.data.width, 
                    annotation.data.height
                );
                break;
                
            case 'circle':
                ctx.beginPath();
                ctx.arc(
                    annotation.data.x, 
                    annotation.data.y, 
                    annotation.data.radius, 
                    0, 
                    2 * Math.PI
                );
                ctx.stroke();
                break;
                
            case 'text':
                ctx.font = `${annotation.lineWidth * 4}px Arial`;
                ctx.fillText(annotation.data.text, annotation.data.x, annotation.data.y);
                break;
                
            case 'arrow':
                drawArrow(
                    annotation.data.startX, 
                    annotation.data.startY, 
                    annotation.data.endX, 
                    annotation.data.endY
                );
                break;
        }
    }

    function drawArrow(startX: number, startY: number, endX: number, endY: number) {
        if (!ctx) return;
        
        const headLength = 15;
        const angle = Math.atan2(endY - startY, endX - startX);
        
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.lineTo(
            endX - headLength * Math.cos(angle - Math.PI / 6),
            endY - headLength * Math.sin(angle - Math.PI / 6)
        );
        ctx.moveTo(endX, endY);
        ctx.lineTo(
            endX - headLength * Math.cos(angle + Math.PI / 6),
            endY - headLength * Math.sin(angle + Math.PI / 6)
        );
        ctx.stroke();
    }

    function getMousePos(e: MouseEvent) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY
        };
    }

    function handleMouseDown(e: MouseEvent) {
        if (selectedTool === 'text') {
            const pos = getMousePos(e);
            textPosition = pos;
            showTextInput = true;
            return;
        }
        
        isDrawing = true;
        const pos = getMousePos(e);
        lastX = pos.x;
        lastY = pos.y;
        
        if (selectedTool === 'pen') {
            currentAnnotation = {
                type: 'pen',
                data: { points: [{ x: pos.x, y: pos.y }] },
                color: selectedColor,
                lineWidth: lineWidth
            };
        } else if (selectedTool === 'rectangle' || selectedTool === 'circle') {
            currentAnnotation = {
                type: selectedTool,
                data: { x: pos.x, y: pos.y },
                color: selectedColor,
                lineWidth: lineWidth
            };
        } else if (selectedTool === 'arrow') {
            currentAnnotation = {
                type: 'arrow',
                data: { startX: pos.x, startY: pos.y },
                color: selectedColor,
                lineWidth: lineWidth
            };
        }
    }

    function handleMouseMove(e: MouseEvent) {
        if (!isDrawing || !currentAnnotation) return;
        
        const pos = getMousePos(e);
        
        if (selectedTool === 'pen') {
            currentAnnotation.data.points.push({ x: pos.x, y: pos.y });
        } else if (selectedTool === 'rectangle') {
            currentAnnotation.data.width = pos.x - currentAnnotation.data.x;
            currentAnnotation.data.height = pos.y - currentAnnotation.data.y;
        } else if (selectedTool === 'circle') {
            const dx = pos.x - currentAnnotation.data.x;
            const dy = pos.y - currentAnnotation.data.y;
            currentAnnotation.data.radius = Math.sqrt(dx * dx + dy * dy);
        } else if (selectedTool === 'arrow') {
            currentAnnotation.data.endX = pos.x;
            currentAnnotation.data.endY = pos.y;
        }
        
        redrawCanvas();
        drawAnnotation(currentAnnotation);
    }

    function handleMouseUp() {
        if (isDrawing && currentAnnotation) {
            annotations.push({ ...currentAnnotation });
            currentAnnotation = null;
        }
        isDrawing = false;
    }

    function addText() {
        if (textInput.trim()) {
            const annotation = {
                type: 'text',
                data: { 
                    text: textInput, 
                    x: textPosition.x, 
                    y: textPosition.y 
                },
                color: selectedColor,
                lineWidth: lineWidth
            };
            annotations.push(annotation);
            redrawCanvas();
        }
        textInput = '';
        showTextInput = false;
    }

    function clearAnnotations() {
        annotations = [];
        redrawCanvas();
    }

    function undoLastAnnotation() {
        annotations.pop();
        redrawCanvas();
    }

    function saveAnnotation() {
        if (annotations.length === 0) {
            toast.error('No annotations to save');
            return;
        }
        
        // Convert canvas to base64 image
        const annotatedImageData = canvas.toDataURL('image/png');
        
        dispatch('save', {
            imageData: annotatedImageData,
            annotations: annotations
        });
        
        toast.success('Annotation saved successfully');
        show = false; // Close the modal after saving
    }

    function handleImageLoad() {
        setupCanvas();
    }

    let hasInitialized = false;
    
    $: if (show && !hasInitialized) {
        // Reset only when modal first opens
        annotations = [];
        currentAnnotation = null;
        showTextInput = false;
        hasInitialized = true;
    }
    
    $: if (!show) {
        hasInitialized = false;
    }
    

</script>

<div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[99999]" 
    class:hidden={!show}
    on:click={(e) => {
        // Prevent clicks on the overlay from reaching underlying elements
        e.stopPropagation();
        e.preventDefault();
    }}
>
    <div 
        class="bg-white dark:bg-gray-800 rounded-lg p-4 max-w-6xl max-h-[90vh] overflow-auto"
        on:click={(e) => {
            // Prevent clicks on modal content from reaching underlying elements
            e.stopPropagation();
        }}
    >
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">Annotate Image</h2>
            <button 
                class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                on:click={() => {
                    show = false;
                }}
            >
                ✕
            </button>
        </div>

        <div class="flex gap-4">
            <!-- Tools Panel -->
            <div class="w-48 space-y-4">
                <div>
                    <h3 class="font-semibold mb-2">Tools</h3>
                    <div class="space-y-2">
                        {#each tools as tool}
                            <button
                                class="w-full p-2 text-left rounded border {selectedTool === tool.id ? 'border-blue-500 bg-blue-50 dark:bg-blue-900' : 'border-gray-200 dark:border-gray-600'}"
                                on:click={() => selectedTool = tool.id}
                            >
                                <span class="mr-2">{tool.icon}</span>
                                {tool.name}
                            </button>
                        {/each}
                    </div>
                </div>

                <div>
                    <h3 class="font-semibold mb-2">Colors</h3>
                    <div class="grid grid-cols-4 gap-2">
                        {#each colors as color}
                            <button
                                class="w-8 h-8 rounded border-2 {selectedColor === color ? 'border-gray-800' : 'border-gray-300'}"
                                style="background-color: {color}"
                                on:click={() => selectedColor = color}
                            ></button>
                        {/each}
                    </div>
                </div>

                <div>
                    <h3 class="font-semibold mb-2">Line Width</h3>
                    <input
                        type="range"
                        min="1"
                        max="10"
                        bind:value={lineWidth}
                        class="w-full"
                    />
                    <div class="text-center text-sm">{lineWidth}px</div>
                </div>

                <div class="space-y-2">
                    <button
                        class="w-full p-2 bg-red-500 text-white rounded hover:bg-red-600"
                        on:click={clearAnnotations}
                    >
                        Clear All
                    </button>
                    <button
                        class="w-full p-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                        on:click={undoLastAnnotation}
                        disabled={annotations.length === 0}
                    >
                        Undo Last
                    </button>
                    <div 
                        class="w-full p-2 bg-green-500 text-white rounded hover:bg-green-600 relative z-50 cursor-pointer"
                        on:click={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            saveAnnotation();
                        }}
                    >
                        Save Annotation
                    </div>
                </div>
            </div>

            <!-- Canvas Area -->
            <div class="flex-1">
                <div class="relative border border-gray-300 dark:border-gray-600 rounded overflow-hidden">
                    <canvas
                        bind:this={canvas}
                        class="max-w-full max-h-[70vh] cursor-crosshair"
                        on:mousedown={handleMouseDown}
                        on:mousemove={handleMouseMove}
                        on:mouseup={handleMouseUp}
                        on:mouseleave={handleMouseUp}
                    ></canvas>
                    
                    <img
                        bind:this={imageElement}
                        src={imageSrc}
                        alt={imageAlt}
                        class="hidden"
                        on:load={handleImageLoad}
                    />
                </div>
            </div>
        </div>

        <!-- Text Input Modal -->
        {#if showTextInput}
            <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[999999]">
                <div class="bg-white dark:bg-gray-800 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">Add Text</h3>
                    <input
                        type="text"
                        bind:value={textInput}
                        class="w-full p-2 border rounded mb-2 dark:bg-gray-700 dark:border-gray-600"
                        placeholder="Enter text..."
                        on:keydown={(e) => e.key === 'Enter' && addText()}
                    />
                    <div class="flex gap-2">
                        <button
                            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                            on:click={addText}
                        >
                            Add
                        </button>
                        <button
                            class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                            on:click={() => { showTextInput = false; textInput = ''; }}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        {/if}
    </div>
</div> 