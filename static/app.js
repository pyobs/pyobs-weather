function plot(canvas) {
    // get type and label
    let type = $(canvas).attr('data-sensor-type');
    let label = $(canvas).attr('data-sensor-label');

    // do AJAX request
    $.ajax({
        url: '/api/history/' + type + '/',
        dataType: 'json',
    }).done(function (results) {
        // format data so that Chart.js can digest it
        let plotData = [];
        results.forEach(function (station) {
            // don't plot average values
            if (station.code === 'average')
                return;

            // format data
            let data = [];
            station.data.forEach(function (value) {
                data.push({t: new moment.utc(value.time).format('YYYY-MM-DD HH:mm:ss'), y: value.value})
            });

            // create plot dict
            plotData.push({
                label: station.name,
                data: data,
                backgroundColor: station.color,
                borderColor: station.color,
                pointBorderColor: station.color,
                pointBackgroundColor: station.color,
                pointRadius: 1,
                fill: false,
                lineTension: 0.2
            });
        });

        // create plot
        new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                datasets: plotData
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            tooltipFormat: 'YYYY-MM-DD HH:mm.ss',
                            displayFormats: {
                                millisecond: 'HH:mm',
                                second: 'HH:mm',
                                minute: 'HH:mm',
                                hour: 'HH:mm'
                            }
                        },
                        distribution: 'linear',
                        scaleLabel: {
                            display: true,
                            labelString: 'Time [UT]',
                        }
                    }],
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: label
                        }
                    }]
                }
            }
        });

    });
}

function update_plots() {
    // do all plots
    $(".plot").each(function (index) {
        plot(this);
    });

    // schedule next run
    setTimeout(update_values, 60000);
}

function update_values() {
    // do AJAX request
    $.ajax({
        url: '/api/current/',
        dataType: 'json',
    }).done(function (results) {
        // loop all fields on page
        $(".sensorValue").each(function (index) {
            // get type
            let value_field = $(this);
            let type = value_field.attr('data-sensor-type');

            // got a value?
            if (results.hasOwnProperty('sensors') && results.sensors.hasOwnProperty(type) &&
                    results.sensors[type].value !== null) {
                value_field.html(results.sensors[type].value.toFixed(1));
            } else {
                value_field.html('N/A');
            }

            // good?
            let color = 'black';
            if (results.hasOwnProperty('sensors') && results.sensors.hasOwnProperty(type)) {
                if (results.sensors[type].good === true) {
                    color = 'green';
                }
                if (results.sensors[type].good === false) {
                    color = 'red';
                }
            }
            value_field.css('color', color);
        });

        // set time
        if (results.hasOwnProperty('time')) {
            $('#time').html(moment.utc(results.time).format('HH:mm:ss'));
        }
    });

    // schedule next run
    setTimeout(update_values, 10000);
}

$(function () {
    update_plots();
    update_values();
});
