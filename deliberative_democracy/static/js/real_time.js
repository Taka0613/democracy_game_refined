var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('project_completed', function(data) {
    // Refresh the project list and scoreboard
    location.reload();
});
