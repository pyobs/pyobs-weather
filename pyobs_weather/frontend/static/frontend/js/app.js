function addAlpha(color, opacity) {
    // coerce values so ti is between 0 and 1.
    var _opacity = Math.round(Math.min(Math.max(opacity || 1, 0), 1) * 255);
    return color + _opacity.toString(16).toUpperCase();
}

function plot_dict(station, values, agg_type) {
    // create plot dict
    return {
        label: agg_type === 'mean' ? station.name : '',
        data: values,
        backgroundColor: addAlpha(station.color, 0.1),
        borderColor: addAlpha(station.color, 0.5),
        //pointBorderColor: station.color,
        //pointBackgroundColor: station.color,
        pointRadius: 0,
        borderWidth: agg_type === "mean" ? 3 : -1,
        fill: agg_type === 'max' ? '-1' : 0,
        lineTension: 0.2,
    }
}

function create_plot(canvas, datasets, annotations) {
    // get type and label
    let type = $(canvas).attr('data-sensor-type');
    let label = $(canvas).attr('data-sensor-label');
    datasets = datasets ? datasets : [];
    annotations = annotations ? annotations : {};

    // create plot
    return new Chart(canvas.getContext('2d'), {
        type: 'line',
        data: { datasets: datasets },
        options: {
            plugins: {
                legend: {
                    labels: {
                        filter: function (label) {
                            return label.text !== '';
                        }
                    }
                },
                annotation: {
                    annotations: annotations
                }
            },
            animation: {
                duration: 0
            },
            scales: {
                //bounds: 'ticks',
                x: {
                    source: 'auto',
                    type: 'time',
                    time: {
                        tooltipFormat: 'yyyy-MM-dd HH:mm.ss',
                        displayFormats: {
                            millisecond: 'HH:mm',
                            second: 'HH:mm',
                            minute: 'HH:mm',
                            hour: 'HH:mm'
                        }
                    },
                    min: moment.utc().subtract(1, 'days').format('YYYY-MM-DD HH:mm:ss'),
                    max: moment.utc().format('YYYY-MM-DD HH:mm:ss'),
                    distribution: 'linear',
                    title: {
                        display: true,
                        text: 'Time [UT]',
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: label
                    },
                    ticks: {
                        callback: function (value) {
                            return value.toFixed(1);
                        }
                    }
                }
            }
        }
    });
}

function plot(canvas, chart) {
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
            let v = [], vmin = [], vmax = [];
            station.data.forEach(function (value) {
                v.push({x: new moment.utc(value.time).format('YYYY-MM-DD HH:mm:ss'), y: value.value})
                vmin.push({x: new moment.utc(value.time).format('YYYY-MM-DD HH:mm:ss'), y: value.min})
                vmax.push({x: new moment.utc(value.time).format('YYYY-MM-DD HH:mm:ss'), y: value.max})
            });

            // add
            plotData.push(plot_dict(station, v, "mean"));
            plotData.push(plot_dict(station, vmin, "min"));
            plotData.push(plot_dict(station, vmax, "max"));

        });

        // annotations
        let annotations = [];
        results.areas.forEach(function (area) {
            // init annotation
            let ann = {
                type: 'box',
                display: true,
                yScaleID: 'y',
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

        // set annotations and update
        chart.data.datasets = plotData;
        chart.options.plugins.annotation.annotations = annotations;
        chart.update();
    });
}

function create_plots() {
    // do all plots
    let plots = [];
    $(".plot").each(function (index) {
        let chart = create_plot(this);
        plots.push({canvas: this, chart: chart});
    });
    return plots;
}

function update_plots(plots) {
    // do all plots
    plots.forEach(function (value, index) {
        plot(value.canvas, value.chart);
    });
    //$(".plot").each(function (index) {
    //    plot(this);
    //});

    // schedule next run-
    setTimeout(update_plots.bind(null, plots), 60000);
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

function create_good_annotation(good) {
    return {
        type: 'box',
        display: true,
        xScaleID: 'x',
        yScaleID: 'y',
        drawTime: 'beforeDatasetsDraw',
        borderWidth: 0,
        backgroundColor: good ? 'rgba(0, 255, 0, 0.5)' : 'rgba(255, 0, 0, 0.5)'
    }
}

function create_good_history() {
    // create plot
    return new Chart($('#goodhistory')[0].getContext('2d'), {
        type: 'line',
        data: {
            datasets: []
        },
        options: {
            animation: {
                duration: 0
            },
            plugins: {
                legend: {
                    display: false
                },
                annotation: {
                    annotations: {}
                }
            },
            scales: {
                //bounds: 'ticks',
                x: {
                    type: 'time',
                    source: 'auto',
                    distribution: 'linear',
                    time: {
                        tooltipFormat: 'yyyy-MM-dd HH:mm.ss',
                        displayFormats: {
                            millisecond: 'HH:mm',
                            second: 'HH:mm',
                            minute: 'HH:mm',
                            hour: 'HH:mm'
                        }
                    },
                    min: moment.utc().subtract(1, 'days').format('YYYY-MM-DD HH:mm:ss'),
                    max: moment.utc().format('YYYY-MM-DD HH:mm:ss'),
                    title: {
                        display: true,
                        text: 'Time [UT]',
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Sun/good'
                    },
                }
            },
        }
    });
}
function plot_good_history(chart) {
    // do AJAX request
    $.ajax({
        url: rootURL + 'api/history/goodweather/',
        dataType: 'json',
    }).done(function (results) {
        // format data
        let data = [];
        results.sun.time.forEach(function (value, index) {
            data.push({x: new moment.utc(value).format('YYYY-MM-DD HH:mm:ss'), y: results.sun.alt[index]})
        });

        // annotations
        let annotations = [];
        for (let i = 0; i < results.changes.length; i++) {
            // get change
            let change = results.changes[i];

            // first one needs an additional annotation
            if (i === 0) {
                let ann = create_good_annotation(!change.good);
                ann.xMax = moment.utc(change.time).format('YYYY-MM-DD HH:mm:ss');
                annotations.push(ann);
            }

            // min/max depends on first/last
            let ann = create_good_annotation(change.good);
            ann.xMin = moment.utc(change.time).format('YYYY-MM-DD HH:mm:ss');
            if (results.changes.length > i + 1) {
                ann.xMax = moment.utc(results.changes[i + 1].time).format('YYYY-MM-DD HH:mm:ss');
            }
            annotations.push(ann);
        }

        // add annotation for line at 0
        annotations.push({
            type: 'line',
            mode: 'horizontal',
            scaleID: 'y',
            value: 0,
            borderColor: 'rgb(0, 0, 0, 0.5)',
            borderWidth: 1
        })

        chart.data.datasets = [{
                label: undefined,
                data: data,
                backgroundColor: 'rgb(255, 255, 100, 0.5)',
                borderColor: 'rgb(255, 255, 100, 1)',
                pointRadius: 0,
                fill: false,
                lineTension: 0.2,
            }]
        chart.options.plugins.annotation.annotations = annotations;
        chart.update();
    });
}

function update_good_history(chart) {
    plot_good_history(chart);
    setTimeout(update_good_history.bind(0, chart), 60000);
}

$(function () {
    //Chart.defaults.global.defaultFontFamily = 'Alegreya';

    $(window).on('resize', draw_timeline);
    update_timeline();
    let plots = create_plots();
    update_plots(plots);
    let good = create_good_history();
    update_good_history(good);
    update_values();
});
