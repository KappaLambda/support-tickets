$(document).ready(function() {
    $(".clickable-row").on("click", function() {
        window.location.href = $(this).attr("href");
    });
});
