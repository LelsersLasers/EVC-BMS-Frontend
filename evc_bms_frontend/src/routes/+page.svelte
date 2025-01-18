<script>
    import { onMount } from 'svelte';
    import Modal from '$lib/Modal.svelte';

    let ipAddress = $state(null);
    let displayIpAddress = $state(null);
    let showIpAddressModal = $state(false);
    let ipAddressInput = $state('');
    let ipAddressError = $state(null);
    let name = $state("disconnected...");

    $effect(() => {
        if (!ipAddress) return;
        else if (ipAddress.startsWith('http://')) displayIpAddress = ipAddress.slice(7);
        else displayIpAddress = ipAddress;
    })

    let loading = $state(false);

    let data = $state({});


    onMount(async () => {
        const ls = localStorage.getItem('ipAddress');
        if (ls) {
            ipAddressInput = ls;
            validateIpAddressInput();
        }
    });

    function validateIpAddressInput() {
        if (ipAddressInput == "") return;

        let ip = ipAddressInput;

        if (!ip.startsWith('http://')) ip = `http://${ip}`;
        if (ip.endsWith('/'))          ip = ip.slice(0, -1);

        loading = true;

        fetch(`${ip}/name`)
            .then(res => {
                if (!res.ok) throw new Error('');
                return res.text();
            })
            .then(text => {
                name = text;
                ipAddress = ip;
                localStorage.setItem('ipAddress', ip);
                loading = false;
                showIpAddressModal = false;
                ipAddressError = null;
            })
            .catch(e => {
                loading = false;
                showIpAddressModal = true;
                ipAddressError = 'Could not connect to BMS at that IP address';
            });
    }

    function ipAddressDialogClose() {
        showIpAddressModal = false;
        if (ipAddress == null) {
            setTimeout(() => {
                showIpAddressModal = true;
            }, 10);
        }
    }

    $effect(() => {
        if (!showIpAddressModal && ipAddress == null) {
            showIpAddressModal = true;
        }
    });
</script>

<style>
    #navbar {
        display: flex;
        flex-direction: row;
        border-bottom: 1px solid #333;
    }
    #logo {
        display: flex;
        flex-direction: row;

        background-color: #333;
        color: white;
        padding-left: 5px;
        padding-right: 5px;
    }
    #name {
        padding-right: 8px;
        color: #ABD130;
    }
    #ip {
        display: flex;
        align-items: last baseline;
        margin-left: 10px;
        padding-bottom: 5px;
    }
    #address {
        color: #aaa;
    }
    #ipInput {
        width: 100%;
        padding: 8px;
        outline: none !important;
        border: 2px solid #aaa;
        border-radius: 5px;
        margin-bottom: 0.25em;
    }
    #ipInput:focus {
        border: 2px solid #ABD130;
        outline: none !important;
    }
    #connect {
        padding: 8px;
        background-color: #ABD130;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    #connect:disabled {
        background-color: #aaa;
        cursor: not-allowed;
    }

    #all {
        display: grid;
        grid-template-columns: 3fr 1fr;
        grid-gap: 10px;

        padding: 10px;
    }

    #main {
        grid-column: 1;
        outline: 1px solid black;
    }

    #sidebar {
        grid-column: 2;
        outline: 1px solid black;
    }

    .modalTitle {
        margin-bottom: 0.25em;
    }

    #loading {
        width: fit-content;

        font-weight: 400;
        font-style: italic;
        font-size: smaller;

        padding-bottom: 1px;
        background: linear-gradient(currentColor 0 0) 0 100%/0% 3px no-repeat;
        animation: l2 2s linear infinite;

        position: absolute;
        top: 1%;
        right: 1%;
    }
    @keyframes l2 {to{background-size: 100% 3px}}
</style>




<div id="loading" style="display: {loading ? 'block' : 'none'}">Loading...</div>


<div id="navbar">
    <div id="logo">
        <h1 id="name">EVC</h1>
        <h1>BMS</h1>
    </div>
    <div id="ip">
        <span id="address">{name} ({displayIpAddress})</span>
    </div>
</div>

<div id="all">
    <div id="main">
        {#if !ipAddress}
            <p>Waiting for ip address...</p>
        {:else}
            <h2>Connected to BMS at {ipAddress}</h2>
        {/if}
    </div>
    
    <div id="sidebar">
        <p>SIDE BAR</p>
    </div>
</div>




{#snippet ipAddressPrompt()}
    <h2 class="modalTitle">Enter IP of BMS</h2>
    {#if ipAddressError}
        <p style="color: red">{ipAddressError}</p>
    {/if}
    <input id="ipInput" type="text" placeholder="192.168.1.1" bind:value={ipAddressInput} />
    {#if !loading}
        <button id="connect" onclick={validateIpAddressInput}>Connect</button>
    {:else}
        <button id="connect" disabled>Connect</button>
    {/if}
{/snippet}

<Modal showModal={showIpAddressModal} close={ipAddressDialogClose} children={ipAddressPrompt}>
</Modal>