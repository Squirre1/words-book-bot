const getLabels = (stats) => stats.map(({ word}) => word)
const getValues = (stats, value) => stats.map(stat => stat[value])

const drawBarChart = (chartId, labels = [], data = []) => {
    const mychart = document.getElementById(chartId).getContext("2d");

    const barData = {
        type: 'horizontalBar',
        data: {
            labels: labels,
            datasets: [
                {
                    fillColor: "rgba(151,187,205,0.2)",
                    strokeColor: "rgba(151,187,205,1)",
                    pointColor: "rgba(151,187,205,1)",
                    data
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                xAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },
            legend: {
                display: false
            }
        }
    }

    new Chart(mychart, barData);
}

const drawGeneralChart = (chartId, labels = [], data = []) => {
    const mychart = document.getElementById(chartId).getContext("2d");

    const polarData = {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [
                {
                    data,
                    backgroundColor: ['#0000FF', '#0000FF', '#00dd0e', '#00dd0e', '#ff6384', '#ff6384', '#ffce56' ,'#ffce56']
                }
            ]
        },
        options: {
            responsive: true,
            legend: {
                display: true,
                position: 'bottom'
            }
        }
    }

    new Chart(mychart, polarData);
}

const drawRadarChart = (chartId, labels = [], datasets = []) => {
    const mychart = document.getElementById(chartId).getContext("2d");

    const polarData = {
        type: 'radar',
        data: {
            labels: labels,
            datasets
        },
        options: {
            responsive: true,
            legend: {
                display: false
            }
        }
    }

    new Chart(mychart, polarData);
}

const statsArray = Object.keys(statistics || {}).map((word) => ({ word, ...statistics[word] }))
const sessionsArray = Object.keys(sessions || {}).map((sessionId) => ({ sessionId, ...sessions[sessionId] }))

const reminders = statsArray.sort((p,n) => n.reminders - p.reminders).slice(0,5)
setTimeout(() => drawBarChart('reminders', getLabels(reminders), getValues(reminders, 'reminders')), 0)

const asked = statsArray.sort((p,n) => n.asked - p.asked).slice(0,5)
setTimeout(() => drawBarChart('asked', getLabels(asked), getValues(asked, 'asked')), 0)

const generalLabels = ['asked', 'VVasked', 'guessings', 'VVguessings', 'mistakes', 'VVmistakes', 'reminders', 'VVreminders']
const generalValues = statsArray.reduce((acc, value) => acc.map((stat, index) => stat + (value[generalLabels[index]] || 0 )), [0, 0, 0, 0, 0, 0, 0, 0])
setTimeout(() => drawGeneralChart('general', generalLabels, generalValues), 0)

if (sessionsArray.length >= 2) {
    const lastSessions = sessionsArray.sort((p,n) => n.sessionId - p.sessionId).slice(0,2)
    const sessionsValues = lastSessions.map((session, i) => ({ data: generalLabels.map(label => session.stats[label])}))
    setTimeout(() => drawRadarChart('sessions', generalLabels, sessionsValues), 0)
}
