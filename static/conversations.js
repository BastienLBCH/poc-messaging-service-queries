function createConversationBox(item) {
    var conversationColumn = document.getElementById("conversationsColumn");

    var conversationBox = document.createElement("div")
    conversationBox.classList.add("box");
    conversationBox.setAttribute('conversationId', item['id']);
    conversationBox.appendChild(document.createTextNode(item['name']));

    conversationColumn.appendChild(conversationBox);
    conversationBox.addEventListener("click", getMessages);
}


function clearConversationColumn() {
    var conversationColumn = document.getElementById("conversationsColumn");

    for (var i=0; i<conversationColumn.children.length; i++) {
        if(i >= conversationColumn.children.length) {
            break;
        }
        if(conversationColumn.children[i].classList.contains("box")) {
            conversationColumn.children[i].remove();
            i--;
        }
    }
}


function getConversations() {
    var myHeaders = new Headers()
    var conversationColumn = document.getElementById("conversationsColumn");

    clearConversationColumn();

    myHeaders.append('Authorization', 'Bearer '+accessToken);

    let url = window.location.href + "conversations";

    fetch(
        url,
        {
            method: 'GET',
            headers: myHeaders
        }
    )
        .then(response => response.json())
        .then(response => {
            response.forEach((item, index) => {
                createConversationBox(item);
            });
        })
        .catch(function (error) {
            console.log(error.message);
        });
}


async function createConversation() {
    event.preventDefault();

    var conversationNameField = document.getElementById("conversationField");

    var myHeaders = new Headers();
    myHeaders.append('Authorization', 'Bearer '+accessToken);
    myHeaders.append('Accept', '*/*')
    myHeaders.append('Content-Type', 'application/json')

    var data = {
        name: conversationNameField.value
    }

    var url = `${commandServer}/conversations/`;


    conversationNameField.value = "";


    const response = await fetch(
        url,
        {
            method: 'POST',
            headers: myHeaders,
            body: JSON.stringify(data)
        }
    ).catch((error) => console.log(error));
}


