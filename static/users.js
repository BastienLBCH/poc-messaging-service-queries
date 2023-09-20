async function addUser(event) {
    event.preventDefault();

    var userIdField = document.getElementById("userIdField");
    var selectedConversation = document.getElementsByClassName("selectedConversation")[0];

    var myHeaders = new Headers();
    myHeaders.append('Authorization', 'Bearer '+accessToken);
    myHeaders.append('Accept', '*/*')
    myHeaders.append('Content-Type', 'application/json')

    var data = {
        participant_id: userIdField.value
    };

    userIdField.value = "";

    var conversationId = selectedConversation.getAttribute("conversationId");
    var url = `${commandServer}/conversations/${conversationId}/participants`;

    const response = await fetch(
        url,
        {
            method: 'POST',
            headers: myHeaders,
            body: JSON.stringify(data)
        }
    ).catch((error) => console.log(error));
}

function createUserBox(user){
    var usersListDiv = document.getElementById("usersListDiv");

    var userBox = document.createElement("div");

    userBox.classList.add("box")

    var boxContent = `${user['username']} : ${user['id']}`;
    userBox.appendChild(document.createTextNode(boxContent));

    usersListDiv.appendChild(userBox);
}

async function listUsers() {
    var usersListDiv = document.getElementById("usersListDiv");
    usersListDiv.classList.toggle("is-hidden");

    for(var i=0; i<usersListDiv.children.length; i++) {
        if(i >= usersListDiv.children.length) {
            break;
        }
        if(usersListDiv.children[i].classList.contains("box")) {
            usersListDiv.children[i].remove();
            i--;
        }
    }

    var myHeaders = new Headers();
    myHeaders.append('Authorization', 'Bearer '+accessToken);

    var response = await fetch(keycloakUsersUrl, {headers:myHeaders}).catch((error) => {console.log(error)});
    var users = await response.json();

    for(const user of users) {
        createUserBox(user);
    }
}

function hideListUsers() {
    var usersListDiv = document.getElementById("usersListDiv");
    usersListDiv.classList.toggle("is-hidden");
}