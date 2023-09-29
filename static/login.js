function giveInterface() {
    let loginDiv = document.getElementById("loginDiv");
    loginDiv.classList.toggle("is-hidden");
    getConversations();
    startwebsocket();
}

window.addEventListener('DOMContentLoaded', () => {
    let loginDiv = document.getElementById("loginDiv");
    let loginForm = document.getElementById("loginForm");

    if(userIsLoggedIn === true) {
        giveInterface();
    }

    // loginDiv.innerHTML = keycloakTokenUrl + loginDiv.innerHTML;

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        var myHeaders = new Headers()
        myHeaders.append('Content-Type', 'application/x-www-form-urlencoded');

        var data = new URLSearchParams();
        data.append('client_id', clientId);
        data.append('grant_type', 'password');
        data.append('username', document.getElementById('usernameField').value);
        data.append('password', document.getElementById('passwordField').value);

        var response = await fetch(
            keycloakTokenUrl,
            {
                method: 'POST',
                headers: myHeaders,
                body: data
            }
        );

        var serverResponse = await response.json()

        console.log(serverResponse);
        accessToken = serverResponse["access_token"];
        refreshToken = serverResponse["access_token"];
        userIsLoggedIn = true;


        myHeaders = new Headers();
        myHeaders.append('Authorization', `Bearer ${serverResponse['access_token']}` )
        response = await fetch(
            access_url + "/decodetoken",
            {
                headers: myHeaders,
                method: 'GET'
            }
        )


        giveInterface();


    });

});