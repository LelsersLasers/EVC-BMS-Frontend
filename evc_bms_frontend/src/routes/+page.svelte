<script>
    import { onMount } from 'svelte';
    import Modal from '$lib/Modal.svelte';
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    const DATA_FETCH_TIME = 5 * 1000; // 5 seconds [also need to change fetchTimer animation duration]
    const V_MIN = 2.8; // 3.0
    const V_MAX = 4.4; // 4.2
    const T_MIN = 20;
    const T_MAX = 40;
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
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
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    let loading = $state(0);
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    let dataLoopInterval = null;
    let data = $state({});
    let error = $state(null);
    let voltageBarSets = $state([]);
    let temperatureBarSet = $state({});

    let state = $state(null);
    let bypass = $state(null);
    // ---------------------------------------------------------------------- //


    // ---------------------------------------------------------------------- //
    onMount(async () => {
        const ls = localStorage.getItem('ipAddress');
        if (ls) {
            ipAddressInput = ls;
            validateIpAddressInput();
        }
    });

    function validateIpAddressInput() {
        if (ipAddressInput == "") {
            showIpAddressModal = true;
            ipAddressError = "Could not connect to saved Ip address";
            return;
        }

        let ip = ipAddressInput;

        if (!ip.startsWith('http://')) ip = `http://${ip}`;
        if (ip.endsWith('/')) ip = ip.slice(0, -1);

        loading++;
        ipAddressError = null;

        fetch(`${ip}/name`)
            .then((res) => {
                if (!res.ok) throw new Error('');
                return res.text();
            })
            .then((text) => {
                name = text;
                ipAddress = ip;
                localStorage.setItem('ipAddress', ip);
                loading--;
                showIpAddressModal = false;
                ipAddressError = null;
                setTimeout(setupAfterConnected, 10);
            })
            .catch((e) => {
                loading--;
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
    // ---------------------------------------------------------------------- //

    
    // ---------------------------------------------------------------------- //
    function setupAfterConnected() {
        fetchData(); // set interval doesn't run immediately
        setInterval(fetchData, DATA_FETCH_TIME);
    }

    function fetchData() {
        loading++;

        fetch(`${ipAddress}/data`)
            .then((res) => res.json())
            .then((d) => {
                // ---------------------------------------------------------- //
                loading--;
                error = null;

                data = d;
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                if (state == null) state   = d["state"];
                if (bypass == null) bypass = d["bypass"];
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                // TODO: current
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //            
                voltageBarSets = [];

                voltageBarSets["overview"] = {
                    name: "Voltage Overview",
                    bars: [],
                };
                voltageBarSets["overview"]["bars"][0] = { label: "avg", v: d["avg"].toFixed(2) };
                voltageBarSets["overview"]["bars"][1] = { label: "max", v: d["max"].toFixed(2) };
                voltageBarSets["overview"]["bars"][2] = { label: "min", v: d["min"].toFixed(2) };

                for (let i = 0; i < d["cells"].length; i++) {
                    voltageBarSets[i] = {
                        name: `Pack ${i} Voltages`,
                        bars: [],
                    };
                    for (let j = 0; j < d["cells"][i].length; j++) {
                        voltageBarSets[i]["bars"].push({ label: j, v: d["cells"][i][j] });
                    }
                }
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                temperatureBarSet = {
                    name: "Temperatures",
                    bars: [],
                };

                temperatureBarSet["bars"] = [];
                for (let key in d["therm"]) {
                    temperatureBarSet["bars"].push({ label: key, v: d["therm"][key] });
                }
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                data["ready"] = true;
                // ---------------------------------------------------------- //
            })
            .catch((e) => {
                loading--;
                console.error(e);
                error = e;
            });
    }
    // ---------------------------------------------------------------------- //


    // ---------------------------------------------------------------------- //
    function stateParameter(e) {
        loading++;

        fetch(`${ipAddress}/state/${e.target.value}`)
            .then((res) => res.text())
            .then((text) => {
                loading--;
                state = text;
            })
            .catch((e) => {
                loading--;

                console.error(e);
                error = e;
            });
    }

    function bypassParameter(e) {
        loading++;

        console.log("aaaaaa", e.target.checked);

        fetch(`${ipAddress}/bypass/${e.target.checked ? 'enable' : 'disable'}`)
            .then((res) => res.text())
            .then((text) => {
                loading--;
                bypass = text == 'enable';
            })
            .catch((e) => {
                loading--;

                console.error(e);
                error = e;
            });
    }

    function shutdownButton() {
        if (!window.confirm('Are you sure you want to shutdown the BMS?')) return;

        loading++;

        fetch(`${ipAddress}/fullShutdown`)
            .then((res) => res.text())
            .then((text) => {
                loading--;
                state = text;
            })
            .catch((e) => {
                loading--;

                console.error(e);
                error = e;
            });
    }
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    function voltageWidth(v) {
        return (v - V_MIN) / (V_MAX - V_MIN) * 100;
    }

    function temperatureWidth(v) {
        return (v - T_MIN) / (T_MAX - T_MIN) * 100;
    }
    // ---------------------------------------------------------------------- //
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
    }
    /* #holder {} */
    #summaries {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        gap: 5px;
        margin-bottom: 5px;
    }
    .summary {
        width: 50%;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 5px;
    }
    .pack {
        border: 1px solid #333;
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 5px;
    }
    .bar {
        border-radius: 5px;
        transition: width 0.2s linear;
        margin: 0;
        padding: 0;
        padding-top: 0.1em;
        padding-bottom: 0.1em;
        min-width: 20px;
        max-width: 100%;
        
        background-color: #ABD130;
    }
    /* .barText {} */
    


    #sidebar {
        grid-column: 2;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 5px;
    }
    select {
        width: 100%;
        padding: 2px;
        outline: none !important;
        border: 2px solid #aaa;
        border-radius: 5px;
        margin-bottom: 0.25em;
        cursor: pointer;
    }
    select:focus {
        border: 2px solid #ABD130;
        outline: none !important;
    }
    #bypassDiv {
        display: flex;
        flex-direction: row;
        gap: 5px;
    }
    #bypassLabel {
        cursor: pointer;
    }
    #bypass {
        cursor: pointer;
        transform: translateY(0.66px);
        accent-color: #ABD130;
    }
    #shutdownButton {
        width: 100%;
        padding: 8px;
        background-color: #aaa;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    #shutdownButton:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }

    .modalTitle {
        margin-bottom: 0.25em;
    }

    /* div {
        border: 1px solid red;
    } */

    span {
        white-space: nowrap;
        text-wrap: none;
        margin-left: 6px;
        padding-top: 0.1em;
    }

    .error {
        color: red;
    }

    #loading {
        width: fit-content;

        font-weight: 400;
        font-style: italic;
        font-size: smaller;

        padding-bottom: 1px;
        background: linear-gradient(currentColor 0 0) 0 100%/0% 3px no-repeat;
        animation: loading 2s linear infinite;

        position: absolute;
        top: 1%;
        right: 1%;
    }
    @keyframes loading {
        to { background-size: 100% 3px }
    }

    #fetchTimer {
        width: 0%;
        animation: fetchTimer 5s linear infinite;
        border: 2px solid #ABD130;
        border-radius: 5px;
    }
    @keyframes fetchTimer {
        from { width: 0%;   }
        to   { width: 100%; }
    }
</style>




<div id="loading" style="display: {loading != 0 ? 'block' : 'none'}">Fetching...</div>


<div id="navbar">
    <div id="logo">
        <h1 id="name">EVC</h1>
        <h1>BMS</h1>
    </div>
    <div id="ip">
        <span id="address">{name} ({displayIpAddress})</span>
    </div>
</div>

{#if !ipAddress}
    <p>Waiting for ip address...</p>
{:else if !data["ready"]}
    <p>Loading...</p>
{:else}
    <div id="all">
        <div id="main">
            <div id="holder">
                <div id="summaries"> <!-- Voltage overview and temperatures in horizontal -->
                    <div class="summary">
                        <h2>Voltage Overview</h2>
                        <div class="bars">
                            {#each voltageBarSets["overview"].bars as bar (bar.label)}
                                <div class="bar" style="width: {voltageWidth(bar.v)}%">
                                    <span class="barText">{bar.v}V ({bar.label})</span>
                                </div>
                            {/each}
                        </div>
                    </div>

                    <div class="summary">
                        <h2>Temperatures</h2>
                        <div class="bars">
                            {#each temperatureBarSet.bars as bar (bar.label)}
                                <div class="bar" style="width: {temperatureWidth(bar.v)}%">
                                    <span class="barText">{bar.v}°C ({bar.label})</span>
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>

                <div id="packs"> <!-- Voltage of each pack in vertical -->
                    {#each voltageBarSets as pack (pack.name)}
                        <div class="pack">
                            <h2>{pack.name}</h2>
                            <div class="bars">
                                {#each pack.bars as bar (bar.label)}
                                    <div class="bar" style="width: {voltageWidth(bar.v)}%">
                                        <span class="barText">{bar.v}V ({bar.label})</span>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
        
        <div id="sidebar">
            <hr id="fetchTimer" />

            {#if error}
                <p class="error">{error}</p>
                <hr />
            {/if}


            <div>
                <h2>State</h2>
                <select id="stateSelect" bind:value={state} onchange={stateParameter} disabled={loading != 0}>
                    <option value="idle">Idle</option>
                    <option value="monitor">Monitor</option>
                    <option value="charging">Charging</option>
                </select>

                <h2>Bypass</h2>
                <div id="bypassDiv">    
                    <label id="bypassLabel" for="bypass">Enabled</label>
                    <input type="checkbox" id="bypass" bind:checked={bypass} onchange={bypassParameter} disabled={loading != 0} />
                </div>
                {#if data["anyBypassed"]}
                    <p class="error">Bypass triggered</p>
                {/if}

                <h2>Shutdown</h2>
                <button id="shutdownButton" onclick={shutdownButton} type="button" disabled={loading != 0}>Full Shutdown</button>
            </div>
        </div>
    </div>
{/if}





{#snippet ipAddressPrompt()}
    <h2 class="modalTitle">Enter IP of BMS</h2>
    {#if ipAddressError}
        <p class="error">{ipAddressError}</p>
    {/if}
    <!-- svelte-ignore a11y_autocomplete_valid -->
    <input id="ipInput" type="text" placeholder="192.168.1.1" autocomplete="ip" bind:value={ipAddressInput} />
    {#if !loading}
        <button id="connect" onclick={validateIpAddressInput}>Connect</button>
    {:else}
        <button id="connect" disabled>Connect</button>
    {/if}
{/snippet}

<Modal showModal={showIpAddressModal} close={ipAddressDialogClose} children={ipAddressPrompt}>
</Modal>
