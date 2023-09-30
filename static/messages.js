async function getMessageAuthor(user_id) {
    var myHeaders = new Headers();
    myHeaders.append('Authorization', 'Bearer '+accessToken);


    response = await fetch(keycloakUsersUrl + user_id, {headers: myHeaders, method: 'GET'}).catch((error) => console.log(error.message));
    var user = await response.json();
    return user['username'];
}

function addMessageToConversation(username, content, messageId) {
    var messagesColumn = document.getElementById("messagesColumn");
    var messageForm = document.getElementById("messageForm");

    var conversationBox = document.createElement("div")
    conversationBox.classList.add("notification");
    conversationBox.classList.add("messageBox");
    conversationBox.setAttribute('messageId', messageId);

    var boxContent = `${username} : ${content}`;
    conversationBox.appendChild(document.createTextNode(boxContent));
    messagesColumn.insertBefore(conversationBox, messageForm);

    messagesColumn.scrollTo({top: messagesColumn.scrollHeight, left: 0});
    // messagesColumn.appendChild(conversationBox);
}

async function changeSelectedConversation(currentlySelectedConversation) {
    var previouslySelectedConversation = document.getElementsByClassName("selectedConversation");
    if (previouslySelectedConversation.length > 0) {
        previouslySelectedConversation[0].classList.remove("has-background-success-light");
        previouslySelectedConversation[0].classList.remove("selectedConversation");
    }
    currentlySelectedConversation.classList.add("selectedConversation");
    currentlySelectedConversation.classList.add("has-background-success-light");
}

async function getMessages(event){
    var currentlySelectedConversation = event.target;
    await changeSelectedConversation(currentlySelectedConversation);

    var myHeaders = new Headers();
    myHeaders.append('Authorization', 'Bearer '+accessToken);

    var messagesColumn = document.getElementById("messagesColumn");
    var messagesLoaded = document.getElementsByClassName("messageBox");


    console.log(messagesColumn.children.length);


    for (var i=0; i<messagesColumn.children.length; i++) {
        if(i >= messagesColumn.children.length) {
            break;
        }
        if(messagesColumn.children[i].classList.contains("messageBox")) {
            messagesColumn.children[i].remove();
            i--;
        }
    }


    // Get all messages then populates message column
    var element = event.target;
    let url = access_url + "/conversations/" + element.getAttribute('conversationId');

    // variable users is used to associate the user's id with the username
    let users = {};
    var response = await  fetch(url, {method: 'GET', headers: myHeaders});
    var messages = null;
    messages = await response.json();

    for(const message of messages) {
        // if unable to get username from user, display its id
        if(!(message['user_id'] in users)) {
            users[message['user_id']] = await getMessageAuthor(message['user_id']);
        }


        var username = users[message['user_id']]
        var content = message['content']

        addMessageToConversation(username, content, message['id']);
    }
}


async function sendMessage(event) {
    event.preventDefault();

    var selectedConversationId = document.getElementsByClassName("selectedConversation")[0].getAttribute("conversationId");
    var messageField = document.getElementById("messageField")
    var messageContent = messageField.value;

    var myHeaders = new Headers();
    myHeaders.append('Authorization', 'Bearer '+accessToken);
    myHeaders.append('Accept', '*/*')
    myHeaders.append('Content-Type', 'application/json')

    var data = {
        message_content: messageContent
    }

    // var url = `${commandServer}/conversations/sendmessages/`;
    var url = `${commandServer}/conversations/${selectedConversationId}`;

    messageField.value = "";


    const response = await fetch(
        url,
        {
            method: 'POST',
            headers: myHeaders,
            body: JSON.stringify(data)
        }
    ).catch((error) => console.log(error));
}

