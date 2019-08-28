function plot(el, type, label) {
    $.ajax({
        url: '/api/history/' + type + '/',
        dataType: 'json',
    }).done(function (results) {
        let plot = [];
        results.forEach(function (station) {
            let data = [];
            station.data.forEach(function (value) {
                data.push({t: new Date(value.time), y: value.value})
            });
            plot.push({
                label: station.name,
                data: data,
                pointBorderColor: station.color,
                pointBackgroundColor: station.color,
                borderColor: station.color,
                fill: false
            });
            // , 'YYYY-MM-DDTHH:mm:ss.SSZ'
        });

        let ctx = el.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                datasets: plot
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
    $(".plot").each(function (index) {
        let type = $(this).attr('data-sensor-type');
        let label = $(this).attr('data-sensor-label');
        console.log($(this));
        plot($(this), type, label);
    });
});
