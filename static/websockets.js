function startwebsocket() {
    // start websocket
    var baseurl = access_url.replace("http", "ws");
    var url = `${baseurl}/ws/${accessToken}`;

    socket = new WebSocket(url);

    socket.addEventListener("open", (event) => {
        console.log("Websocket connected");
    });

    socket.addEventListener("message", websocketReceivedMessageFromServer);

    socket.addEventListener("error", (event) => {
        console.log("WebSocket error: ", event);
    });

    socket.addEventListener("close", (event) => {
        console.log("Websocket closed")
    });
}

async function websocketReceivedMessageFromServer(event) {
    /*
    Get websocket sent from the server then update the frontend depending on the event
     */
    var eventData = JSON.parse(event.data)
    var systemEvent = eventData["event"];

    switch (systemEvent) {
        case 'userSentMessageToConversation':
            var conversationId = eventData["conversation_id"];
            var selectedConversation = document.getElementsByClassName("selectedConversation")[0];
            if (conversationId === selectedConversation.getAttribute('conversationId')) {
                var message_author = await getMessageAuthor(eventData['user_id']);

                addMessageToConversation(message_author, eventData['message_content'], eventData['id']);
            }
            break;
        case 'userCreatedConversation':
            createConversationBox(eventData);
            break;

        case 'userAddedParticipantToConversation':
            getConversations();
            break;
        default:
            console.log("Unknown event");
    }
}

