<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import Modal from '../common/Modal.svelte';
    import { WEBUI_BASE_URL } from '$lib/constants';
    import { uploadFile } from '$lib/apis/files';
    import { toast } from 'svelte-sonner';

    interface ConvertedImage {
        data: string;
        slice_index: number;
    }

    export let show = false;
    export let mhdFile: { id: string; name: string } | null = null;
    export let rawFile: { id: string; name: string } | null = null;

    const dispatch = createEventDispatcher();

    let selectedSlices: number[] = [];
    let convertedImages: ConvertedImage[] = [];
    let loading = false;
    let imageLoadErrors: { [key: number]: boolean } = {};

    async function convertToImages() {
        loading = true;
        imageLoadErrors = {};
        try {
            // Log file details
            console.log('File Details:', {
                mhdFile: {
                    id: mhdFile?.id,
                    name: mhdFile?.name
                },
                rawFile: {
                    id: rawFile?.id,
                    name: rawFile?.name
                }
            });

            // Call backend to convert CT files to images
            const response = await fetch(`${WEBUI_BASE_URL}/api/v1/ct/convert?mhd_filename=${mhdFile?.id}_${mhdFile?.name}&raw_filename=${rawFile?.id}_${rawFile?.name}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.token}`
                }
            });

            const data = await response.json();
            convertedImages = data.images;
            console.log('Converted Images:', convertedImages);
            // Add debug logging for image data
            convertedImages.forEach((img, i) => {
                console.log(`Image ${i} data length:`, img.data.length);
            });
        } catch (error) {
            console.error('Error converting CT files:', error);
        } finally {
            loading = false;
        }
    }

    function selectSlice(index: number) {
        if (selectedSlices.includes(index)) {
            selectedSlices = selectedSlices.filter(i => i !== index);
        } else {
            selectedSlices = [...selectedSlices, index];
        }
        console.log('Selected Slices:', selectedSlices);
    }

    async function confirmSelection() {
        loading = true;
        try {
            // Create an array of selected image files
            const selectedImageFiles = await Promise.all(selectedSlices.map(async (index) => {
                // Get the base64 image data
                const imageData = convertedImages[index].data;
                
                // Convert base64 to blob
                const response = await fetch(imageData);
                const blob = await response.blob();
                
                // Create a file object
                const file = new File([blob], `ct_slice_${index + 1}.png`, {
                    type: 'image/png'
                });

                return file;
            }));

            // Dispatch the select event with the files
            dispatch('select', { 
                slices: selectedSlices,
                files: selectedImageFiles
            });
            show = false;
        } catch (error) {
            console.error('Error preparing CT scan images:', error);
            toast.error('Failed to prepare CT scan images');
        } finally {
            loading = false;
        }
    }

    function handleImageError(index: number) {
        console.error(`Failed to load image ${index}`);
        imageLoadErrors[index] = true;
    }

    function handleImageLoad(index: number) {
        console.log(`Successfully loaded image ${index}`);
        imageLoadErrors[index] = false;
    }

    // Convert files when popup opens
    $: if (show && mhdFile && rawFile) {
        convertToImages();
    }
</script>

<Modal bind:show size="xl">
    <div class="p-4" tabindex="0">
        <h2 class="text-xl font-bold mb-4">Select CT Scan Slices</h2>

        {#if loading}
            <div class="flex justify-center items-center h-64">
                <p>Converting CT scan to images...</p>
            </div>
        {:else if convertedImages.length > 0}
            <div class="grid grid-cols-4 gap-4 mb-4">
                {#each convertedImages as image, i}
                    <div 
                        class="relative cursor-pointer border rounded p-2 {selectedSlices.includes(i) ? 'border-blue-500' : ''}"
                        on:click={() => selectSlice(i)}
                        tabindex="0"
                        role="button"
                        aria-label="Select slice {i + 1}"
                    >
                        {#if imageLoadErrors[i]}
                            <div class="w-full h-32 flex items-center justify-center bg-gray-100">
                                <p class="text-red-500">Failed to load image</p>
                            </div>
                        {:else}
                            <img 
                                src={image.data} 
                                alt={`Slice ${i + 1}`} 
                                class="w-full h-auto" 
                                on:error={() => handleImageError(i)}
                                on:load={() => handleImageLoad(i)}
                            />
                        {/if}
                        <div class="absolute top-2 right-2">
                            {#if selectedSlices.includes(i)}
                                <div class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center">
                                    ✓
                                </div>
                            {/if}
                        </div>
                    </div>
                {/each}
            </div>

            <div class="flex justify-end gap-2">
                <button 
                    class="px-4 py-2 bg-gray-200 rounded"
                    on:click={() => show = false}
                >
                    Cancel
                </button>
                <button 
                    class="px-4 py-2 bg-blue-500 text-white rounded"
                    on:click={confirmSelection}
                    disabled={selectedSlices.length === 0}
                >
                    Confirm Selection
                </button>
            </div>
        {:else}
            <div class="text-center p-4">
                <p>No images available</p>
            </div>
        {/if}
    </div>
</Modal>