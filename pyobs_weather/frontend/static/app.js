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
            let data = [];
            station.data.forEach(function (value) {
                data.push({t: new Date(value.time), y: value.value})
            });
            plotData.push({
                label: station.name,
                data: data,
                pointBorderColor: station.color,
                pointBackgroundColor: station.color,
                borderColor: station.color,
                fill: false
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
                        distribution: 'linear',
                        scaleLabel: {
                            display: true,
                            labelString: 'Time [UT]'
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
