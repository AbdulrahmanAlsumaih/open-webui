<script lang="ts">
    import { onMount, createEventDispatcher, getContext } from 'svelte';
    import { WEBUI_BASE_URL } from '$lib/constants';
    import type { Writable } from 'svelte/store';
    import type { i18n as i18nType } from 'i18next';
    import ImageAnnotation from './ImageAnnotation.svelte';

    interface CTFile {
        id: string;
        name: string;
        meta?: {
            raw_file_id?: string;
        };
    }

    interface ConvertedImage {
        data: string;
        slice_index: number;
    }

    export let item: CTFile;
    const dispatch = createEventDispatcher();
    const i18n = getContext<Writable<i18nType>>('i18n');

    let loading = true;
    let error: string | null = null;
    let convertedImages: ConvertedImage[] = [];
    let selectedSlice = 0;
    let annotation = '';
    let showAnnotationTool = false;
    let annotatedImageData: string | null = null;

    async function loadImages() {
        try {
            loading = true;
            error = null;
            
            // Log the request details
            console.log('Starting CT conversion with files:', {
                mhdFile: {
                    id: item.id,
                    name: item.name
                },
                rawFile: {
                    id: item.meta?.raw_file_id,
                    name: item.name.replace('.mhd', '.raw')
                }
            });

            const url = `${WEBUI_BASE_URL}/api/v1/ct/convert?mhd_filename=${item.id}_${item.name}&raw_filename=${item.meta?.raw_file_id}_${item.name.replace('.mhd', '.raw')}`;
            console.log('Conversion URL:', url);
            
            // Call backend to convert CT files to images
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.token}`
                }
            });

            console.log('Conversion response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Conversion failed:', errorText);
                throw new Error(`Failed to convert CT files: ${response.statusText}. ${errorText}`);
            }

            const data = await response.json();
            console.log('Conversion response data:', data);
            
            if (!data.images || !Array.isArray(data.images)) {
                throw new Error('Invalid response format: images array not found');
            }

            convertedImages = data.images;
            console.log('Converted Images:', convertedImages);
            
            // Log the first image data length to verify it's correct
            if (convertedImages.length > 0) {
                console.log('First image data length:', convertedImages[0].data.length);
            }
        } catch (err) {
            console.error('Error loading CT images:', err);
            error = err instanceof Error ? err.message : 'Failed to load CT images';
        } finally {
            loading = false;
        }
    }

    function handleImageError(index: number) {
        console.error(`Failed to load image ${index}`);
        error = `Failed to load slice ${index + 1}. Please try again.`;
    }

    function handleImageLoad(index: number) {
        console.log(`Successfully loaded image ${index}`);
        error = null;
    }

    function changeSlice(e: Event) {
        const target = e.target as HTMLInputElement;
        selectedSlice = +target.value;
    }

    function submit() {
        dispatch('select', { 
            sliceIndex: selectedSlice, 
            annotation,
            annotatedImage: annotatedImageData 
        });
    }

    function handleAnnotationSave(event: CustomEvent) {
        annotatedImageData = event.detail.imageData;
        showAnnotationTool = false;
    }

    function openAnnotationTool() {
        showAnnotationTool = true;
    }

    onMount(() => {
        loadImages();
    });
</script>

<div class="space-y-2">
    {#if loading}
        <div class="flex justify-center items-center h-64">
            <p>Loading CT scan images...</p>
        </div>
    {:else if error}
        <div class="text-red-500 p-4 text-center">
            <p class="font-semibold">Error Loading CT Scan</p>
            <p class="text-sm mt-1">{error}</p>
            <button 
                class="mt-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                on:click={loadImages}
            >
                Retry
            </button>
        </div>
    {:else if convertedImages.length > 0}
        <div class="relative">
            <img 
                src={convertedImages[selectedSlice].data} 
                alt={`Slice ${selectedSlice + 1}`} 
                class="w-full h-auto border rounded"
                on:error={() => handleImageError(selectedSlice)}
                on:load={() => handleImageLoad(selectedSlice)}
            />
            {#if convertedImages.length > 1}
                <input 
                    type="range" 
                    min="0" 
                    max={convertedImages.length - 1} 
                    bind:value={selectedSlice} 
                    on:input={changeSlice} 
                    class="w-full mt-2" 
                />
                <div class="text-center text-sm text-gray-500 mt-1">
                    Slice {selectedSlice + 1} of {convertedImages.length}
                </div>
            {/if}
        </div>
        <div class="flex gap-2 mb-2">
            <button 
                class="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 flex items-center gap-1"
                on:click={openAnnotationTool}
            >
                ✏️ Annotate Image
            </button>
            {#if annotatedImageData}
                <span class="text-green-600 text-sm flex items-center">✓ Annotated</span>
            {/if}
        </div>
        
        <textarea 
            bind:value={annotation} 
            class="w-full border rounded p-1 mb-2" 
            placeholder={$i18n.t('Add text annotation')}
        ></textarea>
        
        <div class="flex gap-2">
            <button 
                class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700" 
                on:click={submit}
            >
                {$i18n.t('Use Slice')}
            </button>
        </div>
    {:else}
        <div class="text-center p-4">
            <p>No images available</p>
            <button 
                class="mt-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                on:click={loadImages}
            >
                Retry
            </button>
        </div>
    {/if}
</div>

<!-- Image Annotation Tool -->
<ImageAnnotation
    bind:show={showAnnotationTool}
    imageSrc={convertedImages[selectedSlice]?.data || ''}
    imageAlt={`CT Scan Slice ${selectedSlice + 1}`}
    on:save={handleAnnotationSave}
/>
