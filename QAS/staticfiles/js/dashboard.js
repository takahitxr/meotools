document.addEventListener("DOMContentLoaded", function() {

    var colors = ['#66BB6A', '#A5D6A7', '#FFEB3B', '#FFA726', '#EF5350'];

    // ラベルの要素にデータを動的に挿入
    document.getElementById('verySatisfiedCountLabel').textContent = verySatisfiedCount;
    document.getElementById('satisfiedCountLabel').textContent = satisfiedCount;
    document.getElementById('neutralCountLabel').textContent = neutralCount;
    document.getElementById('dissatisfiedCountLabel').textContent = dissatisfiedCount;
    document.getElementById('veryDissatisfiedCountLabel').textContent = veryDissatisfiedCount;

    // ラベルカラーの設定
    document.getElementById('verySatisfiedColor').style.backgroundColor = colors[0];
    document.getElementById('satisfiedColor').style.backgroundColor = colors[1];
    document.getElementById('neutralColor').style.backgroundColor = colors[2];
    document.getElementById('dissatisfiedColor').style.backgroundColor = colors[3];
    document.getElementById('veryDissatisfiedColor').style.backgroundColor = colors[4];

    var totalCount = verySatisfiedCount + satisfiedCount + neutralCount + dissatisfiedCount + veryDissatisfiedCount;


    // グラフの描画
    var ctx = document.getElementById('reviewChart').getContext('2d');
    var reviewChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            // labels: ['非常に満足', '満足', '普通', '不満', '非常に不満'],
            datasets: [{
                data: [verySatisfiedCount, satisfiedCount, neutralCount, dissatisfiedCount, veryDissatisfiedCount],
                backgroundColor: colors,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    enabled: false
                },
            }
        }
    });

    // マウスオーバー時に該当のセグメントを強調表示
    function highlightSegment(index) {
        reviewChart.setActiveElements([{ datasetIndex: 0, index: index }]);
        reviewChart.update();
    }

    // マウスアウト時に強調を解除
    function resetHighlight() {
        reviewChart.setActiveElements([]);
        reviewChart.update();
    }

    // ラベルにイベントリスナーを追加
    document.getElementById('verySatisfiedColor').addEventListener('mouseenter', function() { highlightSegment(0); });
    document.getElementById('verySatisfiedColor').addEventListener('mouseleave', resetHighlight);

    document.getElementById('satisfiedColor').addEventListener('mouseenter', function() { highlightSegment(1); });
    document.getElementById('satisfiedColor').addEventListener('mouseleave', resetHighlight);

    document.getElementById('neutralColor').addEventListener('mouseenter', function() { highlightSegment(2); });
    document.getElementById('neutralColor').addEventListener('mouseleave', resetHighlight);

    document.getElementById('dissatisfiedColor').addEventListener('mouseenter', function() { highlightSegment(3); });
    document.getElementById('dissatisfiedColor').addEventListener('mouseleave', resetHighlight);

    document.getElementById('veryDissatisfiedColor').addEventListener('mouseenter', function() { highlightSegment(4); });
    document.getElementById('veryDissatisfiedColor').addEventListener('mouseleave', resetHighlight);
});