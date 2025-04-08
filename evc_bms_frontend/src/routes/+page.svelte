<script>
    import { onMount } from "svelte";
    import { slide, fade } from 'svelte/transition';
    import Modal from "$lib/Modal.svelte";
    import NumberInput from "$lib/NumberInput.svelte";
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    const IP = "http://192.168.4.1";
    // const IP = "http://127.0.0.1:5000";
    const DISPLAY_IP = "192.168.4.1";

    const CELLS = 24;

    const START_DATA_FETCH_TIME = 5 * 1000;
    const FETCH_RATE_SET_WAIT = 2 * 1000;
    const CLEAR_SUCCESS_TIME = 5 * 1000; // 5 seconds

    const OVERVIEW_DECIMALS    = 2;
    const VOLTAGE_DECIMALS     = 4;
    const TEMPERATURE_DECIMALS = 1;

    const C_MAX_BALANCING = 25;
    const C_MAX_REGEN = 120;
    const C_MAX_DISCHARGE = 400;

    const V_PADDING = 0.1;
    const T_PADDING = 2;
    const C_PADDING = 1.0;
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    let showSideBar = $state(true);
    let innerW = $state(0);
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    let name = $state(null);
    let connected = $state(false);
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

    let outOfSync = $state("");

    let parameters = $state(null);
    let oldParmeters = $state(null);

    let faults = $state({});
    let pFaults = $state({});

    /*
    parameters = {
        "bypass": false,
        "vBypass": 5.0,

        "vMin": 3.0,
        "vMax": 4.2,
        "vMinAvg": 3.0,
        "vMaxAvg": 4.2,
        "vDiff": 0.2,
        
        "tMin": 10.0,
        "tMax": 50.0,
        "tDiff": 30.0,

        "tMaxBal": 50.0,
        "tResetBal": 40.0,
        "balTempsOk": true, # set

        "logSpeed": 1000,
    };
    */

    let parametersDifferent = $derived(JSON.stringify(parameters) != JSON.stringify(oldParmeters));

    let error  = $state(null);
    let result = $state(null);
    let resultTimeout = null;
    // ---------------------------------------------------------------------- //


    // ---------------------------------------------------------------------- //
    const ALLOWED_FETCH_RATES = [0.5, 1, 2, 5, 10, 15, 30];

    let fetchInt = null;
    let fetchSetInt = null;
    let fetchTimerValue = START_DATA_FETCH_TIME / 1000;

    onMount(async () => {
        fetchData();
        fetchInt = setInterval(fetchData, START_DATA_FETCH_TIME);
    });
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

        fetch(`${IP}/upload`, {
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
    function fetchRateChange(e) {
        const v = ALLOWED_FETCH_RATES.reduce((prev, curr) =>
            Math.abs(curr - e.target.value) < Math.abs(prev - e.target.value)
                ? curr
                : prev
            );

        const fr = document.getElementById("fetchRate");
        fr.value = v;

        const frl = document.getElementById("fetchRateLabel");
        frl.innerHTML = v;

        console.log("rate requested");
        if (fetchSetInt) {
            console.log("rate wait cleared");
            clearTimeout(fetchSetInt);
        }
        console.log("rate wait set");
        fetchSetInt = setTimeout(() => {
            console.log("rate set start");
            fetchData();
            if (fetchInt) {
                fetchTimerValue = v;

                clearInterval(fetchInt);
                console.log("rate set!");
                fetchData();
                fetchInt = setInterval(fetchData, v * 1000);
            }
        }, FETCH_RATE_SET_WAIT);
    }
    // ---------------------------------------------------------------------- //
    
    // ---------------------------------------------------------------------- //
    function fetchData() {
        dataLoading = true;

        const ele = document.getElementById("fetchTimer");
        ele.animate(
            [ { width: "0%" }, { width: "100%" } ],
            {
                duration: fetchTimerValue * 1000,
                easing: "linear",
                fill: "forwards",
            }
        );

        fetch(`${IP}/data`)
            .then((res) => res.json())
            .then((d) => {
                // ---------------------------------------------------------- //
                dataLoading = false;
                error = null;

                connected = true;

                data = d;
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                name = d["name"];
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                if (state == null) {
                    state = d["state"];
                } else {
                    if (d["state"] != state) {
                        outOfSync = "Out of sync! State has been changed on the BMS. Please refresh the page to resync.";
                    } else {
                        outOfSync = "";
                    }
                }

                if (parameters == null) {
                    parameters = d["parameters"];
                    oldParmeters = JSON.parse(JSON.stringify(parameters)); // deep copy
                } else {
                    if (JSON.stringify(d["parameters"]) != JSON.stringify(oldParmeters)) {
                        outOfSync = "Out of sync! Parameters have been changed on the BMS. Please refresh the page to resync.";
                    } else {
                        outOfSync = "";
                    }
                }
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                faults = {};
                for (let key in d["faults"]) {
                    if (d["faults"][key]) {
                        faults[key] = d["faults"][key];
                    }
                }

                pFaults = {};
                for (let key in d["pFaults"]) {
                    if (d["pFaults"][key] && !faults[key]) {
                        pFaults[key] = d["pFaults"][key];
                    }
                }
                // ---------------------------------------------------------- //

                // ---------------------------------------------------------- //
                overviewBarSet = {
                    name: "Overview",
                    bars: [],
                };
                overviewBarSet["bars"][0] = { label: "A (current)", v: d["current"]         .toFixed(OVERVIEW_DECIMALS) };
                overviewBarSet["bars"][1] = { label: "V (avg)",     v: d["avg"]             .toFixed(OVERVIEW_DECIMALS) };
                overviewBarSet["bars"][2] = { label: "V (min)",     v: d["min"]             .toFixed(OVERVIEW_DECIMALS) };
                overviewBarSet["bars"][3] = { label: "V (max)",     v: d["max"]             .toFixed(OVERVIEW_DECIMALS) };
                overviewBarSet["bars"][4] = { label: "V (diff)",    v: (d["max"] - d["min"]).toFixed(OVERVIEW_DECIMALS) };
                overviewBarSet["bars"][5] = { label: "V (total)",   v: d["sum"]             .toFixed(OVERVIEW_DECIMALS) };
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
                            v: d["cells"][i][j].toFixed(VOLTAGE_DECIMALS),
                            discharge: (d["discharge"][i] & (1 << j)) != 0,
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
                        v: d["therm"][key]?.toFixed(TEMPERATURE_DECIMALS)
                    });
                }

                const thermTemps = Object.values(d["therm"]).slice(0, -1);
                const minTemp = Math.min(...thermTemps);
                const maxTemp = Math.max(...thermTemps);
                temperatureBarSet["bars"].push({
                    label: "°C (diff)",
                    v: (maxTemp - minTemp).toFixed(TEMPERATURE_DECIMALS)
                });
                // ---------------------------------------------------------- //
            })
            .catch((e) => {
                dataLoading = false;
                console.warn(e);
                if (e.message == "Failed to fetch") {
                    connected = false;
                } else {
                    error = e;
                }
                connected = false;
            });
    }
    // ---------------------------------------------------------------------- //


    // ---------------------------------------------------------------------- //
    function stateParameter(e) {
        parameterLoading = true;

        fetch(`${IP}/state/${e.target.value}`)
            .then((res) => res.text())
            .then((text) => {
                parameterLoading = false;
                state = text;
                result = `State: ${state}`;
            })
            .catch((e) => {
                parameterLoading = false;
                console.error(e);
                error = e;
            });
    }

    async function saveParameters(e) {
        if (!parametersDifferent) return;

        let r = "";

        for (let key in parameters) {
            if (parameters[key] == oldParmeters[key]) continue;

            parameterLoading = true;

            await fetch(`${IP}/parameters/${key}/${parameters[key]}`)
                .then((res) => res.text())
                .then((text) => {
                    parameterLoading = false;
                    r += `${key}/${parameters[key]}: ${text}`;
                    result = r;
                    oldParmeters[key] = parameters[key];
                })
                .catch((e) => {
                    parameterLoading = false;
                    console.error(e);
                    error = e;
                });
        }
    }

    function deleteLog() {
        if (!window.confirm("Are you sure you want to delete the log file?")) return;

        parameterLoading = true;

        fetch(`${IP}/log/delete`)
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

        fetch(`${IP}/log/download`)
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
        fetch(`${IP}${url}`)
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

        fetch(`${IP}/fullShutdown`)
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

    function acknowledgeFault(fault) {
        parameterLoading = true;

        fetch(`${IP}/acknowledge/${fault}`)
            .then((res) => res.text())
            .then((text) => {
                parameterLoading = false;
                result = `/acknowledge/${fault}: ${text}`;
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

    function calcNotifications(a, b, c) {
        let n = [];
        if (a) n.push(a);
        if (b) n.push(b);
        if (c) n.push(c);
        return n;
    }
    let notifications = $derived(calcNotifications(outOfSync, error, result));
    // ---------------------------------------------------------------------- //

    // ---------------------------------------------------------------------- //
    function calcWidth(v, min, max) {
        return (v - min) / (max - min) * 100;
    }

    function voltageWidth(v) {
        const min = parameters["vMin"] ? parameters["vMin"] : oldParmeters["vMin"];
        const max = parameters["vMax"] ? parameters["vMax"] : oldParmeters["vMax"];
        return calcWidth(v, min - V_PADDING, max + V_PADDING);
    }

    function voltageDiffWidth(v) {
        const max = parameters["vDiff"] ? parameters["vDiff"] : oldParmeters["vDiff"];
        return calcWidth(v, 0, max);
    }

    function voltageTotalWidth(v) {
        const minCell = parameters["vMin"] ? parameters["vMin"] : oldParmeters["vMin"];
        const maxCell = parameters["vMax"] ? parameters["vMax"] : oldParmeters["vMax"];
        const min = minCell * CELLS;
        const max = maxCell * CELLS;
        return calcWidth(v, min - V_PADDING, max + V_PADDING);
    }

    function currentWidth(v) {
        if (state == "balancing") {
            return calcWidth(Math.abs(v), -C_PADDING, C_MAX_BALANCING);
        } else {
            if (v < 0) {
                return calcWidth(-v, -C_PADDING, C_MAX_REGEN);
            } else {
                return calcWidth(v, -C_PADDING, C_MAX_DISCHARGE);
            }
        }
    }

    function temperatureWidth(v) {
        const min = parameters["tMin"] ? parameters["tMin"] : oldParmeters["tMin"];
        const max = parameters["tMax"] ? parameters["tMax"] : oldParmeters["tMax"];
        return calcWidth(v, min - T_PADDING, max + T_PADDING);
    }

    function temperatureDiffWidth(v) {
        const max = parameters["tDiff"] ? parameters["tDiff"] : oldParmeters["tDiff"];
        return calcWidth(v, 0, max);
    }
    // ---------------------------------------------------------------------- //
</script>

<style>
    #navbar {
        display: flex;
        flex-direction: row;
        border-bottom: 1px solid #333;
    }
    #logoHolder {
        width: fit-content;
        background-color: #333;
    }
    #fetchTimer {
        background: #ABD130;
        padding-bottom: 2px;
    }
    /* @keyframes fetchTimer {
        from { width: 0%;   }
        to   { width: 100%; }
    } */
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
        min-width: 2px;
        max-width: 100%;
        background-color: #ABD130;
    }
    .discharge {
        background-color: #90d5ff;
    }
    #current {
        background-color: #4DA6FF;
    }
    .diff {
        background-color: #ff8080;
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

    #fetchRateHolder {
        width: 100%;
        display: flex;
    }
    #fetchRateLabel {
        padding-right: 5px;
    }
    #fetchRate {
        flex: 1;
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
    .saveButton {
        cursor: not-allowed;
    }
    .saveButtonActive {
        background-color: #4DA6FF;
        cursor: pointer;
        animation: bob 1s infinite ease-out;
    }
    @keyframes bob {
        0% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-3px);
        }
        100% {
            transform: translateY(0);
        }
    }

    .sidebarToggle {
        background-color: #333;
        color: white;
        position: absolute;
        top: 62px;
        right: 16px;
        cursor: pointer;
        width: 20px;
        height: 20px;
        border-radius: 5px;
        padding-bottom: 2px;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .sidebarToggle:hover {
        background-color: #555;
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

    .notifications {
        position: fixed;
        top: 1%;
        left: 1%;
        max-width: 25vw;
    }
    .notification {
        background-color: #aaa;
        border: 1px solid #333;
        padding: 8px;
        margin-bottom: 5px;
        border-radius: 5px;
    }

    .stateToolTip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
        line-height: 0.75em;
        font-size: 1.5em;
        margin-top: 0.25em;
    }

    .stateToolTip:after {
        content: "immediate effect";
        position: absolute;
        top: -0.2em;
        right: 0;
        left: 105%;
        display: none;
        text-align: center;
        background-color: #333;
        color: #fff;
        border-radius: 4px;
        padding: 2px;
        font-size: 12px;
        font-style: italic;
        width: 100px;
    }
    .stateToolTip:hover:after {
        display: block;
    }

    .acknowledgeButton {
        background-color: #eee;
        color: #ABD130;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        padding: 0.25em;
        width: fit-content;
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

    @media (max-width: 585px) {
        #all {
            grid-template-columns: 1fr;
            gap: 0;
        }
        #sidebar {
            grid-column: 1;
        }
        .notification {
            width: 80vw;
        }
    }

    .allNoSideBar {
        grid-template-columns: 1fr !important;
    }
</style>



<svelte:window bind:innerWidth={innerW} />



<div id="loading" style="display: {(dataLoading || parameterLoading) ? 'block' : 'none'}">Fetching...</div>


<!-- svelte-ignore a11y_click_events_have_key_events -->
<div id="navbar">
    <div id="logoHolder">
        <div id="fetchTimer">
            <div id="logo">
                <h1 id="name">EVC</h1>
                <h1>BMS</h1>
            </div>
        </div>
    </div>
    <div id="ip">
        <span id="address">{name ? name : "disconnected..."} ({DISPLAY_IP})</span>
    </div>
</div>

{#if !connected}
    <p>Attempting to connect...</p>
{:else}
    <div id="all" class="{showSideBar ? '' : 'allNoSideBar'}">
        <div id="main">
            {#if !showSideBar && innerW >= 585}
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div
                    class="sidebarToggle"
                    onclick={() => showSideBar = true}
                >&#8249;</div>
            {/if}

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
                                {:else if i == overviewBarSet.bars.length - 2}
                                    <div class="bar diff" style="width: {voltageDiffWidth(bar.v)}%">
                                        <div class="span-wrap">
                                            <span class="barV">{bar.v}</span><span class="barLabel">{bar.label}</span>
                                        </div>
                                    </div>
                                {:else if i == overviewBarSet.bars.length - 1}
                                    <div class="bar" style="width: {voltageTotalWidth(bar.v)}%">
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
                            {#each temperatureBarSet.bars as bar, i (bar.label)}
                                {#if i == temperatureBarSet.bars.length - 1}
                                    <div class="bar diff" style="width: {temperatureDiffWidth(bar.v)}%">
                                        <div class="span-wrap">
                                            <span class="barV">{bar.v}</span><span class="barLabel">{bar.label}</span>
                                        </div>
                                    </div>
                                {:else}
                                    <div class="bar" style="width: {temperatureWidth(bar.v)}%">
                                        <div class="span-wrap">
                                            <span class="barV">{bar.v}</span><span class="barLabel">{bar.label}</span>
                                        </div>
                                    </div>
                                {/if}
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
                                    <div
                                        class="bar {bar.discharge ? 'discharge' : ''}"
                                        style="width: {voltageWidth(bar.v)}%"
                                    >
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
        
        {#if showSideBar || innerW < 585}
            <div id="sidebar">
                <!-- {#if outOfSync}
                    <p class="error">
                        Out of sync! Parameters have been changed on the BMS.
                        Please refresh the page to resync.
                    </p>
                    <hr />
                {/if}

                {#if error}
                    <p class="error">{error}</p>
                    <hr />
                {/if}

                {#if result}
                    <p>{@html result}</p>
                    <hr />
                {/if} -->


                <div>
                    {#if innerW >= 585}
                        <!-- svelte-ignore a11y_click_events_have_key_events -->
                        <!-- svelte-ignore a11y_no_static_element_interactions -->
                        <div
                            class="sidebarToggle"
                            onclick={() => showSideBar = false}
                        >&#8250;</div>
                    {/if}

                    <h2>Faults</h2>
                    
                    <h3>Live</h3>
                    {#if Object.keys(faults).length == 0}
                        <p>No faults</p>
                    {:else}
                        {#each Object.keys(faults) as fault}
                            <li class="error">{fault}</li>
                        {/each}
                    {/if}

                    <h3>Persistent</h3>
                    {#if Object.keys(pFaults).length == 0}
                        <p>No persistent faults</p>
                    {:else}
                        {#each Object.keys(pFaults) as fault}
                            <li class="error">
                                {fault}
                                <button
                                    class="acknowledgeButton"
                                    type="button"
                                    onclick={() => acknowledgeFault(fault)}
                                    disabled={parameterLoading}
                                >Acknowledge</button>
                            </li>
                        {/each}
                    {/if}


                    <h2 class="stateToolTip">State</h2>
                    <select id="stateSelect" bind:value={state} onchange={stateParameter} disabled={parameterLoading}>
                        <option value="idle">Idle</option>
                        <option value="monitor">Monitor</option>
                        <option value="balancing">Balancing</option>
                    </select>

                    <h2>Bypass</h2>
                    <div id="bypassDiv">    
                        <label id="bypassLabel" for="bypass">Enabled</label>
                        <input type="checkbox" id="bypass" bind:checked={parameters["bypass"]} disabled={parameterLoading} />
                    </div>
                    {#if parameters["bypass"]}
                        <NumberInput l="Bypass Voltage:" k="vBypass" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    {/if}
                    {#if data["anyBypassed"]}
                        <p class="error">Bypass triggered</p>
                    {/if}

                    <h2>Voltage</h2>
                    <NumberInput l="Cell min:" k="vMin" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    <NumberInput l="Cell max:" k="vMax" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    <NumberInput l="Avg min:" k="vMinAvg" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    <NumberInput l="Avg max:" k="vMaxAvg" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    <NumberInput l="Cell diff:" k="vDiff" p={parameters} op={oldParmeters} pl={parameterLoading} />

                    <h2>Temperature</h2>
                    <NumberInput l="Min:" k="tMin" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    <NumberInput l="Max:" k="tMax" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    <NumberInput l="Temp diff:" k="tDiff" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    {#if data["tDiffTriggered"]}
                        <p class="error">Temperature difference triggered</p>
                    {/if}
                    {#if !data["balTempsOk"] && state == "balancing"}
                        <p class="error">Balance temperature triggered</p>
                    {/if}

                    <h2>Fetch Rate</h2>
                    <div id="fetchRateHolder">
                        <label id="fetchRateLabel" for="fetchRate">5</label>
                        <input type="range" id="fetchRate" name="fetchRate" value="5" min="0.5" max="30" step="0.5" oninput={fetchRateChange} />
                    </div>

                    <h2>Save</h2>
                    <button
                        class="normalButton saveButton {parametersDifferent ? 'saveButtonActive' : ''}"
                        type="button"
                        onclick={saveParameters}
                        disabled={parameterLoading}
                    >Save</button>

                    <h2>File Upload</h2>
                    <button class="normalButton" type="button" onclick={() => showFileUploadModal = true} disabled={parameterLoading}>Upload File</button>

                    <h2>Log file</h2>
                    {#if state == "monitor"}
                        <NumberInput l="Log speed:" k="logSpeed" p={parameters} op={oldParmeters} pl={parameterLoading} />
                    {/if}
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
        {/if}
    </div>
{/if}




{#if notifications && notifications.length > 0}
    <div class="notifications">
        {#each notifications as notification}
            <div
                class="notification"
                in:slide
                out:fade
            >{notification}</div>
        {/each}
    </div>
{/if}


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
