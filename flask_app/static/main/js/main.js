document.addEventListener('DOMContentLoaded', () => {
   const feedbackToggle = document.getElementById('feedback-toggle');
   const feedbackFormContainer = document.getElementById('feedback-form-container');
   const closeFeedbackForm = document.getElementById('close-feedback-form');

   feedbackToggle.addEventListener('click', () => {
       feedbackFormContainer.style.display = 'flex';
   });

   closeFeedbackForm.addEventListener('click', () => {
       feedbackFormContainer.style.display = 'none';
   });

   feedbackFormContainer.addEventListener('click', (event) => {
       if (event.target === feedbackFormContainer) {
           feedbackFormContainer.style.display = 'none';
       }
   });
});
