$(document).ready(function() {
    $('#workout-form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const submitBtn = form.find('button[type="submit"]');
        const resultsDiv = $('#results');
        const errorAlert = $('#error-alert');
        
        // Disable submit button and show loading state
        submitBtn.prop('disabled', true);
        submitBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...');
        
        // Clear previous results and errors
        errorAlert.hide();
        resultsDiv.hide();
        
        $.ajax({
            url: '/track',
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                if (response && response.length > 0) {
                    const resultsBody = $('#results-body');
                    resultsBody.empty();
                    
                    response.forEach(function(exercise) {
                        resultsBody.append(`
                            <tr>
                                <td>${exercise.name}</td>
                                <td>${exercise.duration_min.toFixed(1)}</td>
                                <td>${exercise.nf_calories.toFixed(1)}</td>
                            </tr>
                        `);
                    });
                    
                    resultsDiv.show();
                    form[0].reset();
                } else {
                    errorAlert.text('No exercises found.').show();
                }
            },
            error: function(xhr) {
                let errorMessage = 'An error occurred while processing your request.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                errorAlert.text(errorMessage).show();
            },
            complete: function() {
                // Re-enable submit button and restore original text
                submitBtn.prop('disabled', false);
                submitBtn.html('<i class="bi bi-plus-circle"></i> Add Workout');
            }
        });
    });
});
