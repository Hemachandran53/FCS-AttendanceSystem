// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.bg-blue-100');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Add confirmation for delete actions
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(function(link) {
        if (!link.onclick) {
            link.onclick = function() {
                return confirm('Are you sure you want to delete this item?');
            };
        }
    });

    // Dynamic schedule filtering in add substitution
    const scheduleSelect = document.getElementById('schedule_id');
    const dateInput = document.getElementById('date');
    
    if (scheduleSelect && dateInput) {
        dateInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            const dayName = dayNames[selectedDate.getDay()];
            
            // Filter schedule options based on selected day
            const options = scheduleSelect.querySelectorAll('option');
            options.forEach(function(option) {
                if (option.value && !option.text.includes(dayName) && option.value !== "") {
                                        option.style.display = 'none';
                } else {
                    option.style.display = 'block';
                }
            });
        });
    }

    // Add loading state to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Processing...';
            }
        });
    });

    // Highlight weekend days in schedule tables
    const scheduleTables = document.querySelectorAll('table');
    scheduleTables.forEach(function(table) {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            const cells = row.querySelectorAll('td');
            cells.forEach(function(cell) {
                if (cell.textContent.includes('Saturday') || cell.textContent.includes('Sunday')) {
                    row.classList.add('bg-blue-50');
                }
            });
        });
    });
});