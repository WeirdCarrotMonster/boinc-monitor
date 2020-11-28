<template>
    <div>
        <Host 
            v-for="(hostData, hostKey) in hostInfos"
            :key="hostKey"
            :simpleGuiInfo="hostData"
        />
    </div>
</template>

<script>
import Host from "./Host.vue";
import HostInfoModel from "../dto/HostInfo";

export default {
    name: "BoincResults",
    components: {
        Host
    },
    data() {
        return {
            hostInfos: {},
            resultSource: null,
        };
    },
    mounted() {
        this.resultSource = new EventSource("/results");
        let hostInfos = this.hostInfos;

        this.resultSource.onmessage = function(event) {
            let parsed = JSON.parse(event.data);

            if (parsed.host.name in hostInfos) {
                hostInfos[parsed.host.name].update(parsed)
            } else {
                hostInfos[parsed.host.name] = new HostInfoModel(parsed);
            }
        }
    },
    beforeUnmount() {
        this.resultSource.close()
    }
}
</script>