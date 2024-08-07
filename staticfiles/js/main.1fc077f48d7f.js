$(document).ready(function() {
    $('.star-rating input').on('change', function() {
        var rating = $(this).val();
        $('input[name="rating"]').val(rating);
    });
});

