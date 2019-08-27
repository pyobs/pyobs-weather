$(function () {
    $.ajax({
        url: '/api/history/humid/',
        dataType: 'json',
    }).done(function (results) {
        console.log(results);

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
        console.log(plot);

        var ctx = document.getElementById('myChart').getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: plot
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'time',
                        distribution: 'linear'
                    }]
                }
            }
        });

    });
});
