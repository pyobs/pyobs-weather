$(function () {
    console.log("test");
    let app = new Vue({
        el: '#app',
        delimiters: ['[[', ']]'],
        data: {
            sensors: null,
            time: null
        },
        methods: {
            update() {
                let self = this;
                $.ajax({
                    url: '/api/sensors/',
                    dataType: 'json',
                }).done(function (results) {
                    // store current time
                    self.time = moment.utc().format('YYYY-MM-DD HH:mm:ss');

                    // format time add comments
                    for (let i=0; i<results.length; i++) {
                        // format time
                        if (results[i].since !== null) {
                            results[i].since = moment.utc(results[i].since).format('YYYY-MM-DD HH:mm:ss');
                        }

                        // format value
                        if (results[i].value !== null && results[i].value !== 0 && results[i].value !== 1) {
                            results[i].value = results[i].value.toFixed(1);
                        }

                        // delayed?
                        if (results[i].good_since !== null) {
                            let diff = moment.utc().diff(moment.utc(results[i].good_since)) / 1000;
                            let left = results[i].delay_good - diff;
                            results[i].comment = 'good delayed for ' + left.toFixed(0) + 's';
                        }
                        if (results[i].bad_since !== null) {
                            let diff = results[i].delay_bad - moment.utc().diff(moment.utc(results[i].bad_since)) // 86400000;
                            results[i].comment = 'bad delayed for ' + diff.toFixed(0) + 's';
                        }

                    }

                    // set it
                    self.sensors = results;
                });
            }
        }

    });

    function update() {
        app.update();
        setTimeout(update, 10000);
    }
    update();
});
