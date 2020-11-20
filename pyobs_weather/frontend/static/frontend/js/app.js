function plot(canvas) {
    // get type and label
    let type = $(canvas).attr('data-sensor-type');
    let label = $(canvas).attr('data-sensor-label');

    // do AJAX request
    $.ajax({
        url: rootURL + 'api/history/' + type + '/',
        dataType: 'json',
    }).done(function (results) {
        // format data so that Chart.js can digest it
        let plotData = [];
        results.stations.forEach(function (station) {
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

        // annotations
        let annotations = [];
        results.areas.forEach(function (area) {
            // init annotation
            let ann = {
                type: 'box',
                display: true,
                yScaleID: 'y-axis-0',
                drawTime: 'beforeDatasetsDraw'
            };

            // define colour
            switch (area.type) {
                case 'danger':
                    ann.backgroundColor = 'rgba(255, 0, 0, 0.1)'
                    break;
                case 'warning':
                    ann.backgroundColor = 'rgba(255, 255, 0, 0.1)'
                    break;
            }

            // get min/max values
            if (typeof area.min !== 'undefined') {
                ann.yMin = area.min;
            }
            if (typeof area.max !== 'undefined') {
                ann.yMax = area.max;
            }

            // add annotation
            annotations.push(ann);
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
                },
                annotation: {
                    annotations: annotations
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
        url: rootURL + 'api/current/',
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

        // set goodd
        if (results.hasOwnProperty('good')) {
            let p = $('#good');
            if (results.good === null) {
                p.html('N/A');
                p.css('color', 'black');
            } else {
                p.html(results.good ? 'GOOD' : 'BAD');
                p.css('color', results.good ? 'green' : 'red');
            }
        }

    });

    // schedule next run
    setTimeout(update_values, 10000);
}

function draw_timeline() {
    // get container and canvas
    let container = $('#timeline');
    let canvas = $('#timeline_plot')[0];

    // set size of canvas
    canvas.width = container.innerWidth();

    // get context
    let ctx = canvas.getContext("2d");

    // do AJAX request
    $.ajax({
        url: rootURL + 'api/timeline/',
        dataType: 'json',
    }).done(function (results) {
        // get times
        let now = moment(results['time'])
        let sunset = moment(results['events'][0]);
        let sunset_twilight = moment(results['events'][1]);
        let sunrise_twilight = moment(results['events'][2]);
        let sunrise = moment(results['events'][3]);

        // total length
        let total = sunrise.unix() - sunset.unix();

        // and in pixels
        let px_sunset = 0;
        let px_sunset_twilight = (sunset_twilight.unix() - sunset.unix()) / total * canvas.width;
        let px_sunrise_twilight = (sunrise_twilight.unix() - sunset.unix()) / total * canvas.width;
        let px_sunrise = canvas.width;
        let px_now = (now.unix() - sunset.unix()) / total * canvas.width;

        // draw evening twilight
        let grd1 = ctx.createLinearGradient(0, 0, px_sunset_twilight, 0);
        grd1.addColorStop(0, "yellow");
        grd1.addColorStop(1, "black");
        ctx.fillStyle = grd1;
        ctx.fillRect(px_sunset, 0, px_sunset_twilight - px_sunset, 20);

        // draw morning twilight
        let grd2 = ctx.createLinearGradient(px_sunrise_twilight, 0, px_sunrise, 0);
        grd2.addColorStop(0, "black");
        grd2.addColorStop(1, "yellow");
        ctx.fillStyle = grd2;
        ctx.fillRect(px_sunrise_twilight, 0, px_sunrise - px_sunrise_twilight, 20);

        // night
        ctx.fillStyle = 'black';
        ctx.fillRect(px_sunset_twilight, 0, px_sunrise_twilight - px_sunset_twilight, 20);

        // markers
        ctx.fillStyle = 'white'
        ctx.fillRect(px_sunset_twilight, 0, 2, 20);
        ctx.fillRect(px_sunrise_twilight, 0, 2, 20);
        ctx.fillStyle = 'red'
        ctx.fillRect(px_now, 0, 2, 20);

        // text
        $('#sunset').text('Sunset: ' + sunset.format('HH:mm') + ' UT')
        $('#sunrise').text('Sunrise: ' + sunrise.format('HH:mm') + ' UT')
        $('#sunset_twilight').text('Dusk: ' + sunset_twilight.format('HH:mm') + ' UT')
        $('#sunrise_twilight').text('Dawn: ' + sunrise_twilight.format('HH:mm') + ' UT')

        // text positions
        $('#twilight').css("paddingLeft", px_sunset_twilight - $('#sunset_twilight').width() / 2);
        $('#twilight').css("paddingRight", px_sunrise - px_sunrise_twilight + -$('#sunrise_twilight').width() / 2);
    });
}

function update_timeline() {
    draw_timeline();
    setTimeout(update_timeline, 60000);
}

$(function () {
    Chart.defaults.global.defaultFontFamily = 'Alegreya';

    $(window).on('resize', draw_timeline);
    update_timeline();
    update_plots();
    update_values();
});
