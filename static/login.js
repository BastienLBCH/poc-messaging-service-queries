function giveInterface() {
    let loginDiv = document.getElementById("loginDiv");
    loginDiv.classList.toggle("is-hidden");
    getConversations();
    startwebsocket();
}

window.addEventListener('DOMContentLoaded', () => {
    let loginDiv = document.getElementById("loginDiv");
    let loginForm = document.getElementById("loginForm");

    if(userIsLoggedIn == true) {
        giveInterface();
    }

    // loginDiv.innerHTML = keycloakTokenUrl + loginDiv.innerHTML;

    loginForm.addEventListener("submit", (event) => {
        event.preventDefault();

        var myHeaders = new Headers()
        myHeaders.append('Content-Type', 'application/x-www-form-urlencoded');

        var data = new URLSearchParams();
        data.append('client_id', clientId);
        data.append('grant_type', 'password');
        data.append('username', document.getElementById('usernameField').value);
        data.append('password', document.getElementById('passwordField').value);

        fetch(
            keycloakTokenUrl,
            {
                method: 'POST',
                headers: myHeaders,
                body: data
            }
        )
            .then(response => response.json())
            .then(response => {
                console.log(response);
                accessToken = response["access_token"];
                refreshToken = response["access_token"];
                userIsLoggedIn = true;
                giveInterface();
            });
    });

});