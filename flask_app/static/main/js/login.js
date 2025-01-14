let attemptCount = 0;

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const response = await fetch(form.action, {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    if (result.success) {
        window.location.href = result.redirect;
    } else {
        attemptCount++;
        document.getElementById('login-error').style.display = 'block';
        console.log(`Incorrect attempt count: ${attemptCount}`);
    }
});