<script>
    import { onMount } from 'svelte';

    let ipAddress = $state(null);
    let ipAddressText = $state('No IP address set');

    onMount(async () => {
        const ls = localStorage.getItem('ipAddress');
        if (ls) {
            ipAddress = ls;
        }
    });

    async function promptForIpAddress() {
        let ip = prompt('Enter the IP address of the BMS');
        if (ip) {
            try {
                if (!ip.startsWith('http://')) ip = `http://${ip}`;
                if (ip.endsWith('/'))          ip = ip.slice(0, -1);

                ipAddressText = 'Checking IP address...';

                await fetch(`${ip}/connected`)
                    .then(res => {
                        if (!res.ok) throw new Error('Invalid IP address');
                    });

                ipAddressText = 'No IP address set';

                ipAddress = ip;
                localStorage.setItem('ipAddress', ip);
            } catch (e) {
                alert('Invalid IP address');
                promptForIpAddress();
            }

            localStorage.setItem('ipAddress', ip);
            ipAddress = ip;
        } else {
            alert('You must enter an IP address to continue');
            promptForIpAddress();
        }
    }

    $effect(() => {
        if (!ipAddress) {
            promptForIpAddress();
        }
    });
</script>



<h1>EVC BMS</h1>

{#if ipAddress}
    <p>IP Address: {ipAddress}</p>
{:else}
    <p>{ipAddressText}</p>
{/if}