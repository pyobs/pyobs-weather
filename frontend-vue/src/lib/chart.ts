import Chart from 'chart.js/auto'
import annotationPlugin from 'chartjs-plugin-annotation'
import 'chartjs-adapter-date-fns'

Chart.register(annotationPlugin)

export default Chart
