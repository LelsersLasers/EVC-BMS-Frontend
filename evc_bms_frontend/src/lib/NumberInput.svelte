<script>
    let { l, k, p, op, pl } = $props();
</script>
<style>
    label {
        white-space: nowrap;
        text-wrap: none;
    }

    .labelInputHolder {
        display: flex;
        flex-direction: row;
        gap: 5px;
    }
    .numberInput {
        flex-grow: 1;
        padding-left: 5px;
        outline: none !important;
        border: 2px solid #aaa;
        border-radius: 5px;
    }
    .numberInput:focus {
        border: 2px solid #ABD130;
        outline: none !important;
    }
</style>

<div class="labelInputHolder">
    <label for={k}>{l}</label>
    <input
        class="numberInput"
        type="number"
        name={k}
        placeholder={op[k]}
        bind:value={p[k]}
        disabled={pl}
    />
</div>