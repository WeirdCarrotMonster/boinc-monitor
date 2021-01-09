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
                        {{ activeTask.elapsed_time }}
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
  }
}
</script>

<style scoped>
</style>