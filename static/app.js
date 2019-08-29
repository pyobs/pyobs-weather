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

$(function () {
    // do all plots
    $(".plot").each(function (index) {
        plot(this);
    });
});
