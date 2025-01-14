// Board Modal Functions
function showCreateBoardModal() {
    var modal = document.getElementById('createBoardModal');
    if (modal) {
        modal.style.display = 'block';
        console.log('Modal should be visible now'); // Debug line
    } else {
        console.error('Modal element not found'); // Debug line
    }
}

function closeModal() {
    var modal = document.getElementById('createBoardModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Close modal when clicking outside of it
    window.onclick = function(event) {
        var modal = document.getElementById('createBoardModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});