<template>
    <div class="host-info">
        <table border="1">
            <caption>{{ simpleGuiInfo.name }}</caption>
            <thead>
                <tr>
                    <th>Elapsed</th>
                    <th>State</th>
                    <th>Progress</th>
                    <th>Percent</th>
                </tr>
            </thead>
            <tbody>
                <tr
                    v-for="(activeTask, result) in simpleGuiInfo.results"
                    v-bind:key="result"
                >
                    <td>
                        {{ secondsToTime(activeTask.elapsed_time) }}
                    </td>
                    <td>
                        {{ activeTask.active_task_state }}
                    </td>
                    <td>
                        <progress 
                            max="1" 
                            v-bind:value="activeTask.fraction_done"
                        />
                    </td>
                    <td>
                        {{ Math.floor(activeTask.fraction_done * 100) }}%
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
export default {
  name: 'Host',
  props: {
    simpleGuiInfo: Object
  },
  methods: {
        secondsToTime(timeInSeconds) {
            let pad = function(num, size) { return ('000' + num).slice(size * -1); };
            
            let time = parseFloat(timeInSeconds).toFixed(3);
            let hours = Math.floor(time / 60 / 60);
            let minutes = Math.floor(time / 60) % 60;
            let seconds = Math.floor(time - minutes * 60);

            return pad(hours, 2) + ':' + pad(minutes, 2) + ':' + pad(seconds, 2)
        }
    },
}
</script>

<style scoped>
</style>