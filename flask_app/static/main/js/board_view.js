let socket = io({
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 99999
});

socket.on('connect', () => {
    console.log('Socket connected, joining board...');
    const boardId = window.location.pathname.split('/').pop();
    socket.emit('join_board', { board_id: boardId });
});

socket.on('disconnect', () => {
    console.log('Socket disconnected');
});

socket.on('reconnect', () => {
    console.log('Socket reconnected, rejoining board...');
    const boardId = window.location.pathname.split('/').pop();
    socket.emit('join_board', { board_id: boardId });
});

socket.on('connect_error', (error) => {
    console.log('Connection error:', error);
});

function attachCardListeners(card) {
    const editButton = card.querySelector('.edit-card-button');
    const deleteButton = card.querySelector('.delete-card-button');
    
    if (editButton) {
        const setupEditHandler = (button) => {
            button.addEventListener('click', function editHandler(e) {
                e.stopPropagation();
                const cardContent = card.querySelector('.card-content');
                const currentText = cardContent.textContent;
                
                // Lock the card for editing
                socket.emit('card_editing_started', {
                    board_id: window.location.pathname.split('/').pop(),
                    cardId: card.dataset.cardId
                });
                
                // Change edit button to save button
                button.textContent = 'Save';
                button.classList.remove('edit-card-button');
                button.classList.add('save-card-button');
                
                cardContent.innerHTML = `<textarea class="edit-card-textarea">${currentText}</textarea>`;
                const textarea = cardContent.querySelector('textarea');
                textarea.focus();
                
                // Handle Enter key
                textarea.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        saveChanges();
                    }
                });
                
                const saveChanges = async () => {
                    const newContent = textarea.value.trim();
                    try {
                        const response = await fetch('/update-card', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                cardId: card.dataset.cardId,
                                content: newContent
                            })
                        });
                        
                        if (response.ok) {
                            cardContent.innerHTML = newContent;
                            // Change save button back to edit
                            button.textContent = '✎';
                            button.classList.remove('save-card-button');
                            button.classList.add('edit-card-button');
                            
                            // Unlock the card
                            socket.emit('card_editing_finished', {
                                board_id: window.location.pathname.split('/').pop(),
                                cardId: card.dataset.cardId
                            });
                            
                            // Emit socket event for card update
                            socket.emit('card_updated', {
                                board_id: window.location.pathname.split('/').pop(),
                                cardId: card.dataset.cardId,
                                content: newContent
                            });
                            
                            // Reattach the edit handler
                            setupEditHandler(button);
                            
                        } else {
                            throw new Error('Failed to update card');
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        alert('Failed to update card. Please try again.');
                    }
                };
                
                // Handle save button click
                button.removeEventListener('click', editHandler);
                button.addEventListener('click', function saveHandler() {
                    if (button.classList.contains('save-card-button')) {
                        saveChanges();
                        button.removeEventListener('click', saveHandler);
                    }
                });
            });
        };
        
        // Initial setup of edit handler
        setupEditHandler(editButton);
    }
    
    if (deleteButton) {
        deleteButton.addEventListener('click', async function(e) {
            console.log('Delete button clicked');
            e.stopPropagation();
            if (!confirm('Are you sure you want to delete this card?')) return;
            
            const cardId = card.dataset.cardId;
            
            try {
                const response = await fetch('/delete-card', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        cardId: cardId
                    })
                });
                
                if (response.ok) {
                    card.remove();
                    // Emit socket event for card deletion
                    socket.emit('card_deleted', {
                        board_id: window.location.pathname.split('/').pop(),
                        cardId: cardId
                    });
                } else {
                    throw new Error('Failed to delete card');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to delete card. Please try again.');
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM Content Loaded");  // Debug log
    
    const modal = document.getElementById('addCardModal');
    const closeButton = modal.querySelector('.close-button');
    const addCardForm = document.getElementById('addCardForm');
    const listIdInput = document.getElementById('listId');

    // Add card button click handlers
    console.log("Number of add buttons:", document.querySelectorAll('.add-card-button').length);  // Debug log
    
    document.querySelectorAll('.add-card-button').forEach(button => {
        console.log("Attaching click handler to button");  // Debug log
        button.addEventListener('click', function(e) {
            console.log("Add button clicked!", this.closest('.list').dataset.listId);  // Debug log
            e.stopPropagation();  // Add this to prevent event bubbling
            const listId = this.closest('.list').dataset.listId;
            listIdInput.value = listId;
            modal.style.display = 'block';
        });
    });

    // Close modal when clicking X
    closeButton.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Attach listeners to all existing cards
    document.querySelectorAll('.card').forEach(card => {
        attachCardListeners(card);
    });

    // Handle form submission
    addCardForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted');  // Debug log
        
        const formData = new FormData(this);
        console.log('FormData contents:', {
            listId: formData.get('listId'),
            content: formData.get('cardContent')
        });  // Debug log
        
        try {
            console.log('Sending fetch request to /create-card');  // Debug log
            const response = await fetch('/create-card', {
                method: 'POST',
                body: formData
            });
            
            console.log('Response received:', response);  // Debug log
            
            if (response.ok) {
                const data = await response.json();
                console.log('Response data:', data);  // Debug log
                
                const listId = formData.get('listId');
                const content = formData.get('cardContent');
                const listElement = document.querySelector(`.list[data-list-id="${listId}"] .cards-container`);
                
                const cardElement = document.createElement('div');
                cardElement.className = 'card';
                cardElement.dataset.cardId = data.cardId;  // Use the cardId from response
                cardElement.innerHTML = `
                    <div class="card-content">${content}</div>
                    <div class="card-actions">
                        <button class="edit-card-button" title="Edit card">✎</button>
                        <button class="delete-card-button" title="Delete card">×</button>
                    </div>
                `;
                
                // Attach listeners to the new card
                attachCardListeners(cardElement);
                listElement.appendChild(cardElement);
                
                // Emit socket event for card creation
                socket.emit('card_created', {
                    board_id: window.location.pathname.split('/').pop(),
                    listId: listId,
                    cardId: data.cardId,
                    content: content
                });
                
                // Close modal and reset form
                modal.style.display = 'none';
                this.reset();
            } else {
                const errorData = await response.json();
                console.error('Server error:', errorData);  // Debug log
                throw new Error(`Failed to create card: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Detailed error:', error);  // Debug log
            alert('Failed to create card. Please try again.');
        }
    });

    // Socket.IO and Drag-Drop functionality
    const boardId = window.location.pathname.split('/').pop();
    
    // Join board room
    socket.emit('join_board', { board_id: boardId });
    
    // Listen for card moves from other users
    socket.on('card_moved', function(data) {
        const card = document.querySelector(`[data-card-id="${data.cardId}"]`);
        const newList = document.querySelector(`[data-list-id="${data.listId}"] .cards-container`);
        
        if (card && newList) {
            card.remove();
            const cards = Array.from(newList.children);
            if (data.position >= cards.length) {
                newList.appendChild(card);
            } else {
                newList.insertBefore(card, cards[data.position]);
            }
        }
    });

    // Initialize Sortable for each cards container
    document.querySelectorAll('.cards-container').forEach(container => {
        new Sortable(container, {
            group: 'shared',
            animation: 150,
            ghostClass: 'card-ghost',
            dragClass: 'card-drag',
            
            onEnd: async function(evt) {
                const cardId = evt.item.dataset.cardId;
                const newListId = evt.to.closest('.list').dataset.listId;
                const cards = evt.to.children;
                const newPosition = Array.from(cards).indexOf(evt.item);
                
                try {
                    const response = await fetch('/update-card-position', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            cardId: cardId,
                            listId: newListId,
                            position: newPosition
                        })
                    });
                    
                    if (response.ok) {
                        // Emit socket event for other users
                        socket.emit('card_moved', {
                            board_id: boardId,
                            cardId: cardId,
                            listId: newListId,
                            position: newPosition
                        });
                    } else {
                        throw new Error('Failed to update card position');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Failed to update card position. Please refresh the page.');
                }
            }
        });
    });

    // Add socket listener for card updates
    socket.on('card_updated', function(data) {
        const card = document.querySelector(`[data-card-id="${data.cardId}"]`);
        if (card) {
            const cardContent = card.querySelector('.card-content');
            cardContent.innerHTML = data.content;
        }
    });

    // Add these socket listeners with your other socket.on events
    socket.on('card_created', function(data) {
        console.log('New card created by another user:', data);
        const listElement = document.querySelector(`.list[data-list-id="${data.listId}"] .cards-container`);
        if (listElement) {
            const cardElement = document.createElement('div');
            cardElement.className = 'card';
            cardElement.dataset.cardId = data.cardId;
            cardElement.innerHTML = `
                <div class="card-content">${data.content}</div>
                <div class="card-actions">
                    <button class="edit-card-button" title="Edit card">✎</button>
                    <button class="delete-card-button" title="Delete card">×</button>
                </div>
            `;
            
            // Attach listeners to the new card
            attachCardListeners(cardElement);
            listElement.appendChild(cardElement);
        }
    });

    socket.on('card_deleted', function(data) {
        console.log('Card deleted by another user:', data);
        const card = document.querySelector(`.card[data-card-id="${data.cardId}"]`);
        if (card) {
            card.remove();
        }
    });

    // Add these socket listeners
    socket.on('card_locked', function(data) {
        const card = document.querySelector(`[data-card-id="${data.cardId}"]`);
        if (card) {
            card.classList.add('card-locked');
            const editButton = card.querySelector('.edit-card-button');
            if (editButton) editButton.disabled = true;
            
            // Disable drag for locked cards
            if (card._sortable) {
                card._sortable.option('disabled', true);
            }
        }
    });

    socket.on('card_unlocked', function(data) {
        const card = document.querySelector(`[data-card-id="${data.cardId}"]`);
        if (card) {
            card.classList.remove('card-locked');
            const editButton = card.querySelector('.edit-card-button');
            if (editButton) editButton.disabled = false;
            
            // Re-enable drag for unlocked cards
            if (card._sortable) {
                card._sortable.option('disabled', false);
            }
        }
    });

    // Add this to your existing socket setup
    socket.on('chat_message', function(data) {
        addChatMessage(data.user, data.msg, data.user === currentUser ? 'owner' : 'guest');
    });

    function addChatMessage(user, message, type) {
        const chat = document.getElementById('chat');
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${type}`;
        messageElement.textContent = `${message}`;
        chat.appendChild(messageElement);
        chat.scrollTop = chat.scrollHeight;
    }

    document.getElementById('send-button').addEventListener('click', function() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        if (message) {
            socket.emit('send_message', {
                msg: message,
                board_id: window.location.pathname.split('/').pop()
            });
            input.value = '';
        }
    });

    document.getElementById('message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.getElementById('send-button').click();
        }
    });

    document.querySelector('.toggle-chat').addEventListener('click', function() {
        const chatContent = document.querySelector('.chat-content');
        this.textContent = chatContent.style.display === 'none' ? '□' : '_';
        chatContent.style.display = chatContent.style.display === 'none' ? 'flex' : 'none';
    });
});

// Clean up when leaving the page
window.addEventListener('beforeunload', function() {
    const boardId = window.location.pathname.split('/').pop();
    socket.emit('leave_board', { board_id: boardId });
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('Chat JS loaded');
    
    // Get DOM elements
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    const chat = document.getElementById('chat');
    
    // Verify socket is already defined from earlier in your file
    socket.on('connect', function() {
        console.log('Socket Connected for chat!');
    });

    // Send message click handler
    sendButton.addEventListener('click', function() {
        console.log('Send button clicked');
        const message = messageInput.value.trim();
        console.log('Message content:', message);
        
        if (message !== '') {
            socket.emit('send_message', {'msg': message});
            messageInput.value = '';
        }
    });

    // Message received handler
    socket.on('new_message', function(data) {
        console.log('Message received:', data);
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message';
        messageElement.textContent = data.msg;
        chat.appendChild(messageElement);
        chat.scrollTop = chat.scrollHeight;
    });

    // Enter key handler
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });
});

// When joining the board
socket.on('connect', function() {
    console.log('Socket connected');
    const boardId = window.location.pathname.split('/').pop();
    const userEmail = document.getElementById('user-email').value;
    console.log('Joining board with:', {
        boardId: boardId,
        userEmail: userEmail
    });
    
    socket.emit('join_board', { 
        board_id: boardId,
        user_email: userEmail
    });
});