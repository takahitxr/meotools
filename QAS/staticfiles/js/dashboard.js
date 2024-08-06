document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById('reviewChart').getContext('2d');
    const reviewChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['非常に満足', '満足', '普通', '不満', '非常に不満'],
            datasets: [{
                data: [
                    verySatisfiedCount,
                    satisfiedCount,
                    neutralCount,
                    dissatisfiedCount,
                    veryDissatisfiedCount
                ],
                backgroundColor: ['#4caf50', '#8bc34a', '#ffc107', '#ff9800', '#f44336']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
});