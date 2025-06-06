<script lang="ts">
    import { onMount, createEventDispatcher, getContext } from 'svelte';
    import { WEBUI_API_BASE_URL } from '$lib/constants';

    export let item;
    const dispatch = createEventDispatcher();
    const i18n = getContext('i18n');

    let width = 0;
    let height = 0;
    let depth = 0;
    let sliceIndex = 0;
    let volume: Uint16Array | null = null;
    let annotation = '';
    let canvas: HTMLCanvasElement;

    function parseMeta(text: string) {
        const meta: Record<string, string> = {};
        text.split(/\r?\n/).forEach((line) => {
            const [k, v] = line.split('=');
            if (k && v) meta[k.trim()] = v.trim();
        });
        return meta;
    }

    async function loadVolume() {
        const res = await fetch(`${WEBUI_API_BASE_URL}/files/${item.id}/content`);
        const text = await res.text();
        const meta = parseMeta(text);
        if (meta['DimSize']) {
            const dims = meta['DimSize'].split(/\s+/).map(Number);
            width = dims[0];
            height = dims[1];
            depth = dims[2] || 1;
        }
        const rawId = item.meta?.raw_file_id;
        if (!rawId) {
            console.error('Raw file id not found in metadata');
            return;
        }
        const rawBlob = await fetch(`${WEBUI_API_BASE_URL}/files/${rawId}/content`).then((r) => r.arrayBuffer());
        volume = new Uint16Array(rawBlob);
    }

    function drawSlice() {
        if (!volume) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        const img = ctx.createImageData(width, height);
        const offset = sliceIndex * width * height;
        for (let i = 0; i < width * height; i++) {
            const value = volume[offset + i] / 256; // normalize
            const idx = i * 4;
            img.data[idx] = value;
            img.data[idx + 1] = value;
            img.data[idx + 2] = value;
            img.data[idx + 3] = 255;
        }
        ctx.putImageData(img, 0, 0);
    }

    onMount(async () => {
        await loadVolume();
        drawSlice();
    });

    function changeSlice(e) {
        sliceIndex = +e.target.value;
        drawSlice();
    }

    function submit() {
        dispatch('select', { sliceIndex, annotation });
    }
</script>

<div class="space-y-2">
    <canvas bind:this={canvas} width={width} height={height} class="border rounded"></canvas>
    {#if depth > 1}
        <input type="range" min="0" max={depth - 1} bind:value={sliceIndex} on:input={changeSlice} class="w-full" />
    {/if}
    <textarea bind:value={annotation} class="w-full border rounded p-1" placeholder={$i18n.t('Add annotation')}></textarea>
    <button class="bg-blue-600 text-white px-3 py-1 rounded" on:click={submit}>{$i18n.t('Use Slice')}</button>
</div>
