$(document).ready(function() {
    var socket = io('/chat');
    var user = $('#user').text();

    socket.on('connect', function() {
        console.log('Connected to server');
        socket.emit('joined', {'user': user});
    });

    socket.on('disconnect', function() {
        console.log('Disconnected from server');
    });

    socket.on('status_update', function(data) {
        console.log('Received status update:', data);
        var messageClass = data.style === 'owner' ? 'chat-message owner' : 'chat-message guest';
        var messageElement = $('<div></div>')
            .addClass(messageClass)
            .text(data.msg);
        $('#chat').append(messageElement);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    socket.on('new_message', function(data) {
        console.log('Received message data:', data);
        var messageClass = data.style === 'owner' ? 'chat-message owner' : 'chat-message guest';
        var messageElement = $('<div></div>')
            .addClass(messageClass)
            .text(data.msg);
        $('#chat').append(messageElement);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    $('#send-button').click(function() {
        var messageInput = $('#message-input');
        var message = messageInput.val().trim();
        if (message !== '') {
            console.log('Emitting send_message:', message);
            socket.emit('send_message', {'msg': message});
            messageInput.val('');
        }
    });

    $('#leave-button').click(function() {
        socket.emit('leave', {'user': user});
        socket.disconnect();
        window.location.href = '/';
    });

    $('#message-input').keypress(function(e) {
        if (e.which === 13) {
            $('#send-button').click();
            return false;
        }
    });
});
