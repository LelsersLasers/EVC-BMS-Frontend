<script>
    import { onMount } from "svelte";
    import Modal from "$lib/Modal.svelte";
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    const LS_KEY = "ipAddress";

    const DATA_FETCH_TIME = 5 * 1000; // 5 seconds [also need to change fetchTimer animation duration]
    const CLEAR_SUCCESS_TIME = 5 * 1000; // 5 seconds

    const OVERVIEW_DECIMALS    = 2;
    const VOLTAGE_DECIMALS     = 4;
    const TEMPERATURE_DECIMALS = 1;
    
    const V_MIN = 2.8; // 3.0
    const V_MAX = 4.4; // 4.2
    
    const T_MIN = 20;
    const T_MAX = 40;
    
    const C_MIN = 0;
    const C_MAX = 30;
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    let ipAddress = $state(null);
    let displayIpAddress = $state(null);
    let showIpAddressModal = $state(false);
    let ipAddressInput = $state("");
    let ipAddressError = $state(null);
    let name = $state("disconnected...");

    $effect(() => {
        if (!ipAddress) return;
        else if (ipAddress.startsWith("http://")) displayIpAddress = ipAddress.slice(7);
        else displayIpAddress = ipAddress;
    })
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    let showFileUploadModal = $state(false);
    let file = $state(null);
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    let dataLoading = $state(false);
    let parameterLoading = $state(false);
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    let dataLoopInterval = null;
    let data = $state({});

    let overviewBarSet = $state({});
    let voltageBarSets = $state([]);
    let temperatureBarSet = $state({});

    let state  = $state(null);
    let bypass = $state(null);

    let error   = $state(null);
    let result = $state(null);
    let resultTimeout = null;
    // ---------------------------------------------------------------------- //


    // ---------------------------------------------------------------------- //
    onMount(async () => {
        const ls = localStorage.getItem(LS_KEY);
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

        if (!ip.startsWith("http://")) ip = `http://${ip}`;
        if (ip.endsWith("/")) ip = ip.slice(0, -1);

        parameterLoading = true;
        ipAddressError = null;

        fetch(`${ip}/name`)
            .then((res) => {
                if (!res.ok) throw new Error("");
                return res.text();
            })
            .then((text) => {
                parameterLoading = false;
                name = text;
                ipAddress = ip;
                localStorage.setItem(LS_KEY, ip);
                showIpAddressModal = false;
                ipAddressError = null;
                setTimeout(setupAfterConnected, 10);
            })
            .catch((e) => {
                parameterLoading = false;
                showIpAddressModal = true;
                ipAddressError = "Could not connect to BMS at that IP address";
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

    function triggerDisconnect() {
        if (window.confirm("Are you sure you want to disconnect?")) {
            localStorage.removeItem(LS_KEY);
            window.location.reload();
        }
    }
    // ---------------------------------------------------------------------- //


    // ---------------------------------------------------------------------- //
    function fileUpload(e) {
        e.preventDefault();

        if (!file) {
            alert("Please select a file.");
            return;
        }

        showFileUploadModal = false;
        document.getElementById("fileInput").value = "";
		document.getElementById("fileNameDisplay").textContent = "No file chosen";

        const formData = new FormData();
        formData.append("data", file);

        parameterLoading = true;

        fetch(`${ipAddress}/upload`, {
            method: "POST",
            body: formData,
        })
            .then((res) => res.text())
            .then((text) => {
                parameterLoading = false;
                result = `/upload: ${text}`;
            })
            .catch((e) => {
                parameterLoading = false;
                console.error(e);
                error = e;
            });
    }
    // ---------------------------------------------------------------------- //

    
    // ---------------------------------------------------------------------- //
    function setupAfterConnected() {
        fetchData(); // set interval doesn't run immediately
        setInterval(fetchData, DATA_FETCH_TIME);
    }

    function fetchData() {
        dataLoading = true;

        fetch(`${ipAddress}/data`)
            .then((res) => res.json())
            .then((d) => {
                // ---------------------------------------------------------- //
                dataLoading = false;
                error = null;

                data = d;
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                if (state == null) state   = d["state"];
                if (bypass == null) bypass = d["bypass"];
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                overviewBarSet = {
                    name: "Overview",
                    bars: [],
                };
                overviewBarSet["bars"][0] = { label: "A (current)", v: d["current"].toFixed(OVERVIEW_DECIMALS) };
                overviewBarSet["bars"][1] = { label: "V (avg)",     v: d["avg"]    .toFixed(OVERVIEW_DECIMALS) };
                overviewBarSet["bars"][2] = { label: "V (min)",     v: d["min"]    .toFixed(OVERVIEW_DECIMALS) };
                overviewBarSet["bars"][3] = { label: "V (max)",     v: d["max"]    .toFixed(OVERVIEW_DECIMALS) };
                // ---------------------------------------------------------- //
                voltageBarSets = [];

                for (let i = 0; i < d["cells"].length; i++) {
                    voltageBarSets[i] = {
                        name: `Pack ${i + 1} Voltages`,
                        bars: [],
                    };
                    for (let j = 0; j < d["cells"][i].length; j++) {
                        voltageBarSets[i]["bars"].push({
                            label: `V (${j})`,
                            v: d["cells"][i][j].toFixed(VOLTAGE_DECIMALS)
                        });
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
                    temperatureBarSet["bars"].push({
                        label: `°C (${key})`,
                        v: d["therm"][key].toFixed(TEMPERATURE_DECIMALS)
                    });
                }
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                data["ready"] = true;
                // ---------------------------------------------------------- //
            })
            .catch((e) => {
                dataLoading = false;
                console.error(e);
                error = e;
            });
    }
    // ---------------------------------------------------------------------- //


    // ---------------------------------------------------------------------- //
    function stateParameter(e) {
        parameterLoading = true;

        fetch(`${ipAddress}/state/${e.target.value}`)
            .then((res) => res.text())
            .then((text) => {
                parameterLoading = false;
                state = text;
            })
            .catch((e) => {
                parameterLoading = false;
                console.error(e);
                error = e;
            });
    }

    function bypassParameter(e) {
        parameterLoading = true;

        console.log("aaaaaa", e.target.checked);

        fetch(`${ipAddress}/bypass/${e.target.checked ? "enable" : "disable"}`)
            .then((res) => res.text())
            .then((text) => {
                parameterLoading = false;
                bypass = text == "enable";
            })
            .catch((e) => {
                parameterLoading = false;
                console.error(e);
                error = e;
            });
    }

    function deleteLog() {
        if (!window.confirm("Are you sure you want to delete the log file?")) return;

        parameterLoading = true;

        fetch(`${ipAddress}/log/delete`)
            .then((res) => res.text())
            .then((text) => {
                parameterLoading = false;
                result = `/log/delete: ${text}`;
            })
            .catch((e) => {
                parameterLoading = false;
                console.error(e);
                error = e;
            });
    }

    function downloadLog() {
        parameterLoading = true;

        fetch(`${ipAddress}/log/download`)
            .then((res) => res.blob())
            .then((blob) => {
                parameterLoading = false;

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "evc_bms_log.csv";
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch((e) => {
                parameterLoading = false;
                console.error(e);
                error = e;
            });
    }

    function forceDischarge(enable) {
        if (!window.confirm(`Are you sure you want to ${enable ? "enable" : "disable"} force discharge?`)) return;

        parameterLoading = true;

        let url = `/forceDischarge/${enable ? "enable" : "disable"}`;
        fetch(`${ipAddress}${url}`)
            .then((res) => res.text())
            .then((text) => {
                parameterLoading = false;
                result = `${url}: ${text}`;
            })
            .catch((e) => {
                parameterLoading = false;
                console.error(e);
                error = e;
            });
    }

    function shutdownButton() {
        if (!window.confirm("Are you sure you want to shutdown the BMS?")) return;

        parameterLoading = true;

        fetch(`${ipAddress}/fullShutdown`)
            .then((res) => res.text())
            .then((text) => {
                parameterLoading = false;
                result = `/fullShutdown: ${text}`;
            })
            .catch((e) => {
                parameterLoading = false;
                console.error(e);
                error = e;
            });
    }

    $effect(() => {
        if (result) {
            clearTimeout(resultTimeout);
            resultTimeout = setTimeout(() => {
                result = null;
            }, CLEAR_SUCCESS_TIME);
        }
    });
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    function voltageWidth(v) {
        return (v - V_MIN) / (V_MAX - V_MIN) * 100;
    }

    function currentWidth(v) {
        return (v - C_MIN) / (C_MAX - C_MIN) * 100;
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

    #all {
        display: grid;
        grid-template-columns: 3fr 2fr;

        grid-gap: 10px;

        padding: 10px;
    }

    #main {
        grid-column: 1;
    }
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
    #current {
        background-color: #4DA6FF;
    }


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
    #splitButton {
        display: flex;
        flex-direction: row;
        gap: 5px;
    }

    .normalButton {
        background-color: #ABD130;
        box-shadow: 2px 2px 2px #aaa;
    }
    .normalButton:disabled {
        background-color: #aaa;
        cursor: not-allowed;
        box-shadow: none;
    }

    .dangerButton {
        background-color: #aaa;
        box-shadow: 2px 2px 2px #777;
    }
    .dangerButton:disabled {
        background-color: #ccc;
        cursor: not-allowed;
        box-shadow: none;
    }

    .modalTitle {
        margin-bottom: 0.25em;
    }


    .span-wrap {
        white-space: nowrap;
        text-wrap: none;
    }
    span {
        white-space: nowrap;
        text-wrap: none;
        padding-top: 0.1em;
    }
    .barV {
        margin-left: 6px;
    }
    .barLabel {
        font-size: smaller;
        font-style: italic;
        color: #333;        
    }


    button {
        flex: 1;
        padding: 8px;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
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

    @media (max-width: 585px) {
        #all {
            grid-template-columns: 1fr;
            gap: 0;
        }
        #sidebar {
            grid-column: 1;
        }
    }
</style>




<div id="loading" style="display: {(dataLoading || parameterLoading) ? 'block' : 'none'}">Fetching...</div>


<!-- svelte-ignore a11y_click_events_have_key_events -->
<div id="navbar">
    <div id="logo">
        <h1 id="name">EVC</h1>
        <h1>BMS</h1>
    </div>
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div id="ip" onclick={triggerDisconnect}>
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
                        <h2>Overview</h2>
                        <div class="bars">
                            {#each overviewBarSet.bars as bar, i (bar.label)}
                                {#if i == 0}
                                    <div id="current" class="bar" style="width: {currentWidth(bar.v)}%">
                                        <div class="span-wrap">
                                            <span class="barV">{bar.v}</span><span class="barLabel">{bar.label}</span>
                                        </div>
                                    </div>
                                {:else}
                                    <div class="bar" style="width: {voltageWidth(bar.v)}%">
                                        <div class="span-wrap">
                                            <span class="barV">{bar.v}</span><span class="barLabel">{bar.label}</span>
                                        </div>
                                    </div>
                                {/if}
                            {/each}
                        </div>
                    </div>

                    <div class="summary">
                        <h2>Temperatures</h2>
                        <div class="bars">
                            {#each temperatureBarSet.bars as bar (bar.label)}
                                <div class="bar" style="width: {temperatureWidth(bar.v)}%">
                                    <div class="span-wrap">
                                        <span class="barV">{bar.v}</span><span class="barLabel">{bar.label}</span>
                                    </div>
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
                                        <div class="span-wrap">
                                            <span class="barV">{bar.v}</span><span class="barLabel">{bar.label}</span>
                                        </div>
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

            {#if result}
                <p>{result}</p>
                <hr />
            {/if}


            <div>
                <h2>State</h2>
                <select id="stateSelect" bind:value={state} onchange={stateParameter} disabled={parameterLoading}>
                    <option value="idle">Idle</option>
                    <option value="monitor">Monitor</option>
                    <option value="charging">Charging</option>
                </select>

                <h2>Bypass</h2>
                <div id="bypassDiv">    
                    <label id="bypassLabel" for="bypass">Enabled</label>
                    <input type="checkbox" id="bypass" bind:checked={bypass} onchange={bypassParameter} disabled={parameterLoading} />
                </div>
                {#if data["anyBypassed"]}
                    <p class="error">Bypass triggered</p>
                {/if}

                <h2>File Upload</h2>
                <button class="normalButton" type="button" onclick={() => showFileUploadModal = true} disabled={parameterLoading}>Upload File</button>

                <h2>Log file</h2>
                <div id="splitButton">
                    <button class="normalButton" type="button" onclick={downloadLog} disabled={parameterLoading}>Download Log</button>
                    <button class="dangerButton" type="button" onclick={deleteLog}   disabled={parameterLoading}>Delete Log</button>
                </div>

                <h2>Force Discharge</h2>
                <div id="splitButton">
                    <button class="normalButton" type="button" onclick={() => forceDischarge(true)}  disabled={parameterLoading}>Enable</button>
                    <button class="normalButton" type="button" onclick={() => forceDischarge(false)} disabled={parameterLoading}>Disable</button>
                </div>

                <h2>Shutdown</h2>
                <button class="dangerButton" type="button" onclick={shutdownButton} disabled={parameterLoading}>Full Shutdown</button>
            </div>
        </div>
    </div>
{/if}





{#snippet ipAddressPromptSlot()}
    <h2 class="modalTitle">Enter IP of BMS</h2>
    {#if ipAddressError}
        <p class="error">{ipAddressError}</p>
    {/if}
    <!-- svelte-ignore a11y_autocomplete_valid -->
    <input id="ipInput" type="text" placeholder="192.168.1.1" autocomplete="ip" bind:value={ipAddressInput} />
    {#if !parameterLoading}
        <button class="normalButton" onclick={validateIpAddressInput}>Connect</button>
    {:else}
        <button class="normalButton" disabled>Connect</button>
    {/if}
{/snippet}

<Modal showModal={showIpAddressModal} close={ipAddressDialogClose} children={ipAddressPromptSlot}>
</Modal>


{#snippet fileUploadSlot()}
    <h2 class="modalTitle">Upload File</h2>
    <form onsubmit={fileUpload}>
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div style="display: inline-flex; align-items: center; gap: 0.2em; cursor: pointer; margin-bottom: 0.4em; width: 100%;">
            <div style="position: relative; display: inline-block; cursor: pointer;">
                <label
                    for="fileInput"
                    style="
                        display: inline-block;
                        padding: 0.4em;
                        padding-left: 0.6em;
                        background-color: #ABD130;
                        font-size: 1em;
                        border-radius: 0.5em 0 0 0.5em;
                        cursor: pointer;
                    "
                >
                    Choose File
                </label>
                <input
                    id="fileInput"
                    type="file"
                    style="
                        opacity: 0;
                        position: absolute;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        cursor: pointer;
                    "
                    onchange={(e) => {
                        file = e.target.files[0];
                        document.getElementById("fileNameDisplay").textContent = file.name;
                    }}
                    required
                />
            </div>		  
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <span
                id="fileNameDisplay"
                style="
                    font-size: 14px;
                    color: #45475a;
                    font-style: italic;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    display: inline-block;
                    font-size: 0.9em;
                    cursor: pointer;
                "
                onclick={() => document.getElementById("fileInput").click()}
            >
                No file chosen
            </span>
        </div>
        <br />

        <p>Existing files will be replaced.</p>

        <button class="normalButton" type="submit" disabled={!file}>Upload</button>
    </form>
{/snippet}

<Modal showModal={showFileUploadModal} children={fileUploadSlot}>
</Modal>
