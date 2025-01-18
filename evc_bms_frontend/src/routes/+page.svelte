<script>
    import { onMount } from 'svelte';
    import Modal from '$lib/Modal.svelte';

    let ipAddress = $state(null);
    let name = $state("disconnected...");

    let loading = $state(true);

    let data = $state({});


    // onMount(async () => {
    //     // TODO: valid old IP address
    //     // TODO: not use window prompt, use an input
    //     const ls = localStorage.getItem('ipAddress');
    //     if (ls) {
    //         ipAddress = ls;
    //     }
    // });

    function promptForIpAddress() {
        let ip = prompt('Enter the IP address of the BMS');
        if (ip) {
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
                    })
                    .catch(e => {
                        loading = false;
                        setTimeout(() => {
                            alert('Could not connect to BMS at that IP address');
                            promptForIpAddress();
                        }, 10);
                    });
        } else {
            alert('You must enter an IP address to continue');
            promptForIpAddress();
        }
    }

    // $effect(() => {
    //     if (!ipAddress) {
    //         promptForIpAddress();
    //     }
    // });
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

    #loading {
        width: fit-content;

        font-weight: 400;
        font-style: italic;

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
        <span id="address">{name} ({ipAddress})</span>
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




{#snippet loadingModal()}
    <p>Loading...</p>
{/snippet}

<Modal showModal={loading} children={loadingModal}>
</Modal>