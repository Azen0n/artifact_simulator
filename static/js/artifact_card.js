$(document).ready(function () {
    let draw = SVG();

    let linear = draw.gradient('linear', function (add) {
        add.stop(0, '#5D517E')
        add.stop(1, '#A570A8')
    }).from(0, 0).to(0.8, 1.2);

    draw.path('M 0 5 A 5 5 0 0 1 5 0 L 121 0 A 5 5 0 0 1 126 5 L 126 93 A 30 30 0 0 1 96 123 L 0 123 L 0 5 Z').fill(linear);
    draw.path('M 0 123 L 0 147 A 5 5 0 0 0 5 152 L 121 152 A 5 5 0 0 0 126 147 L 126 93 A 30 30 0 0 1 96 123 Z').fill('#E9E5DC');
});