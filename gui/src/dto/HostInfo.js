export default class HostInfoModel {
    constructor(data) {
        this.name = data.host.name
        this.results = {}

        let results = this.results;
        data.results.forEach(element => {
            results[element.name] = element.active_task
        });
    }
    update(data) {
        let results = this.results;

        let usedKeys = [];
        data.results.forEach(element => {
            results[element.name] = element.active_task
            usedKeys.push(element.name)
        });

        Object.keys(results).forEach(key => {
            if (!usedKeys.includes(key)) {
                delete results[key]
            }
        })
    }
}