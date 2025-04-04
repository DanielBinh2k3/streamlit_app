"""JavaScript utilities for the Streamlit app."""

# JavaScript code for key event handling and other client-side functionality
js_code = """
<script>
// Key event listener for hotkeys
document.addEventListener('keydown', function(e) {
    // Ctrl + Enter for form submission
    if (e.ctrlKey && e.key === 'Enter') {
        const submitButtons = document.querySelectorAll('button[kind="primaryFormSubmit"]');
        if (submitButtons.length > 0) {
            submitButtons[0].click();
        }
    }

    // Forward slash (/) to focus on the input area
    if (e.key === '/' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
        const textAreas = document.querySelectorAll('textarea');
        if (textAreas.length > 0) {
            textAreas[0].focus();
        }
    }
});

// Double-click to focus on input area
document.addEventListener('dblclick', function(e) {
    if (document.activeElement.tagName !== 'TEXTAREA') {
        const textAreas = document.querySelectorAll('textarea');
        if (textAreas.length > 0) {
            textAreas[0].focus();
        }
    }
});

// Function to handle message deletion
function setupDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-message-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const messageId = this.getAttribute('data-message-id');
            if (messageId) {
                window.parent.postMessage({
                    type: 'deleteMessage',
                    messageId: messageId
                }, '*');
            }
        });
    });
}

// Run setup when DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupDeleteButtons();

    // Add observer to handle dynamically added content
    const observer = new MutationObserver(function(mutations) {
        setupDeleteButtons();
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
"""
